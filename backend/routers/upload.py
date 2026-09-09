import shutil
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

import jobs
from pipeline.ffmpeg_utils import probe

router = APIRouter()


@router.post("/api/jobs")
async def upload_video(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(400, "no filename")
    job = jobs.create_job(file.filename)
    ext = Path(file.filename).suffix or ".mp4"
    dest = jobs.job_path(job["id"], f"source{ext}")
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        info = probe(str(dest))
    except Exception as e:
        raise HTTPException(400, f"could not read video: {e}")

    job = jobs.update_job(
        job["id"],
        video={
            "width": info.width,
            "height": info.height,
            "duration": info.duration,
            "fps": info.fps,
            "path": str(dest),
        },
    )
    return job
