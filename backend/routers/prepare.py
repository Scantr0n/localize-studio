from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

import jobs
from config import TARGET_HEIGHT, TARGET_WIDTH
from pipeline.ffmpeg_utils import CropBox, detect_crop, extract_frame, make_working_copy

router = APIRouter()


class PrepareRequest(BaseModel):
    crop: dict | None = None  # {"x":.., "y":.., "w":.., "h":..} manual override


@router.post("/api/jobs/{job_id}/prepare")
async def prepare(job_id: str, req: PrepareRequest | None = None):
    job = jobs.get_job(job_id)
    if job is None:
        raise HTTPException(404, "job not found")
    source_path = job["video"]["path"]
    duration = job["video"]["duration"]

    if req and req.crop:
        c = req.crop
        crop = CropBox(x=c["x"], y=c["y"], w=c["w"], h=c["h"], auto_detected=False)
    else:
        crop = detect_crop(source_path, duration)

    working_path = jobs.job_path(job_id, "working.mp4")
    jobs.update_job(job_id, status="preparing")
    try:
        make_working_copy(source_path, crop, TARGET_WIDTH, TARGET_HEIGHT, str(working_path))
        frame_path = jobs.job_path(job_id, "frame_preview.jpg")
        extract_frame(str(working_path), duration * 0.25, str(frame_path))
    except Exception as e:
        jobs.update_job(job_id, status="error", error=str(e))
        raise HTTPException(500, str(e))

    job = jobs.update_job(
        job_id,
        status="prepared",
        crop={"x": crop.x, "y": crop.y, "w": crop.w, "h": crop.h, "auto_detected": crop.auto_detected},
        working_video={"path": str(working_path), "width": TARGET_WIDTH, "height": TARGET_HEIGHT},
    )
    return job


@router.get("/api/jobs/{job_id}/frame")
async def get_frame(job_id: str):
    path = jobs.job_path(job_id, "frame_preview.jpg")
    if not path.exists():
        raise HTTPException(404, "frame not found")
    return FileResponse(str(path), media_type="image/jpeg")
