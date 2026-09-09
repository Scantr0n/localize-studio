from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

import jobs
from pipeline.ffmpeg_utils import extract_audio
from pipeline.transcribe import transcribe as run_transcribe

router = APIRouter()


class TranscribeRequest(BaseModel):
    language: str | None = "auto"


def _do_transcribe(job_id: str, language: str | None):
    try:
        job = jobs.get_job(job_id)
        working_path = job["working_video"]["path"]
        audio_path = str(jobs.job_path(job_id, "audio.wav"))
        extract_audio(working_path, audio_path)
        segments = run_transcribe(audio_path, language)
        jobs.save_json(job_id, "transcript.json", segments)
        jobs.update_job(job_id, status="transcribed", progress=1.0, transcribe_language=language)
    except Exception as e:
        jobs.update_job(job_id, status="error", error=str(e))


@router.post("/api/jobs/{job_id}/transcribe")
async def transcribe_endpoint(job_id: str, req: TranscribeRequest, background: BackgroundTasks):
    job = jobs.get_job(job_id)
    if job is None:
        raise HTTPException(404, "job not found")
    if not job.get("working_video"):
        raise HTTPException(400, "run /prepare first")
    jobs.update_job(job_id, status="transcribing", progress=0.0)
    background.add_task(_do_transcribe, job_id, req.language)
    return {"status": "transcribing"}


@router.get("/api/jobs/{job_id}/transcript")
async def get_transcript(job_id: str):
    segments = jobs.load_json(job_id, "transcript.json", default=[])
    return {"segments": segments}


class TranscriptUpdate(BaseModel):
    segments: list[dict]


@router.patch("/api/jobs/{job_id}/transcript")
async def update_transcript(job_id: str, req: TranscriptUpdate):
    job = jobs.get_job(job_id)
    if job is None:
        raise HTTPException(404, "job not found")
    jobs.save_json(job_id, "transcript.json", req.segments)
    return {"segments": req.segments}
