import uuid

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

import jobs
from captions.ass_writer import render_ass
from captions.models import CaptionEvent, Canvas, StyleParams
from captions.styles import STYLE_REGISTRY
from pipeline.ffmpeg_utils import burn_subtitles

router = APIRouter()


@router.get("/api/jobs/{job_id}/styles")
async def list_styles(job_id: str):
    return [
        {"id": s.id, "display_name": s.display_name, "needs_anchor": s.needs_anchor}
        for s in STYLE_REGISTRY.values()
    ]


class TrackTag(BaseModel):
    segment_id: int
    text: str


class Track(BaseModel):
    name: str
    style_id: str
    language: str  # "transcript" (original language) or a translation lang code
    palette: list[str] | None = None
    anchor: dict | None = None
    tags: list[TrackTag] = []


class RenderRequest(BaseModel):
    tracks: list[Track]


def _events_for_track(job_id: str, transcript: list[dict], translations: dict, track: Track) -> list[CaptionEvent]:
    events: list[CaptionEvent] = []
    seg_by_id = {s["id"]: s for s in transcript}

    for seg in transcript:
        if track.language == "transcript":
            text = seg["text"]
        else:
            lang_map = translations.get(track.language, {})
            text = lang_map.get(str(seg["id"]))
            if text is None:
                raise ValueError(f"missing translation for segment {seg['id']} in language {track.language}")
        events.append(CaptionEvent(start=seg["start"], end=seg["end"], text=text, kind="main"))

    for tag in track.tags:
        seg = seg_by_id.get(tag.segment_id)
        if seg is None:
            raise ValueError(f"tag references unknown segment {tag.segment_id}")
        events.append(CaptionEvent(start=seg["start"], end=seg["end"], text=tag.text, kind="tag"))

    return events


def _do_render(job_id: str, req: RenderRequest):
    try:
        job = jobs.get_job(job_id)
        working_path = job["working_video"]["path"]
        canvas = Canvas(width=job["working_video"]["width"], height=job["working_video"]["height"])
        transcript = jobs.load_json(job_id, "transcript.json", default=[])
        translations = jobs.load_json(job_id, "translations.json", default={})

        results = []
        for track in req.tracks:
            style = STYLE_REGISTRY.get(track.style_id)
            if style is None:
                raise ValueError(f"unknown style {track.style_id}")
            events = _events_for_track(job_id, transcript, translations, track)
            params = StyleParams(palette=track.palette or [], anchor=track.anchor)
            style_lines, dialogue_lines = style.render(events, canvas, params)
            ass_content = render_ass(canvas.width, canvas.height, style_lines, dialogue_lines)

            render_id = str(uuid.uuid4())[:8]
            ass_path = jobs.job_path(job_id, "renders", f"{track.name}_{render_id}.ass")
            out_path = jobs.job_path(job_id, "renders", f"{track.name}_{render_id}.mp4")
            ass_path.write_text(ass_content, encoding="utf-8")
            burn_subtitles(working_path, str(ass_path), str(out_path))
            results.append({"render_id": render_id, "track_name": track.name, "file": out_path.name})

        renders = jobs.load_json(job_id, "renders.json", default=[])
        renders.extend(results)
        jobs.save_json(job_id, "renders.json", renders)
        jobs.update_job(job_id, status="done", progress=1.0)
    except Exception as e:
        jobs.update_job(job_id, status="error", error=str(e))


@router.post("/api/jobs/{job_id}/render")
async def render_endpoint(job_id: str, req: RenderRequest, background: BackgroundTasks):
    job = jobs.get_job(job_id)
    if job is None:
        raise HTTPException(404, "job not found")
    if not job.get("working_video"):
        raise HTTPException(400, "run /prepare first")
    jobs.update_job(job_id, status="rendering", progress=0.0)
    background.add_task(_do_render, job_id, req)
    return {"status": "rendering"}


@router.get("/api/jobs/{job_id}/renders")
async def list_renders(job_id: str):
    return jobs.load_json(job_id, "renders.json", default=[])


@router.get("/api/jobs/{job_id}/renders/{filename}/download")
async def download_render(job_id: str, filename: str):
    path = jobs.job_path(job_id, "renders", filename)
    if not path.exists():
        raise HTTPException(404, "render not found")
    return FileResponse(str(path), media_type="video/mp4", filename=filename)
