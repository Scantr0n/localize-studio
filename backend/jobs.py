import json
import time
import uuid
from pathlib import Path
from threading import Lock

from config import JOBS_DIR

_lock = Lock()
_jobs: dict[str, dict] = {}


def _job_dir(job_id: str) -> Path:
    return JOBS_DIR / job_id


def _job_json_path(job_id: str) -> Path:
    return _job_dir(job_id) / "job.json"


def create_job(source_filename: str) -> dict:
    job_id = str(uuid.uuid4())
    d = _job_dir(job_id)
    (d / "renders").mkdir(parents=True, exist_ok=True)
    job = {
        "id": job_id,
        "status": "uploaded",
        "progress": 0.0,
        "error": None,
        "source_filename": source_filename,
        "video": None,
        "crop": None,
        "created_at": time.time(),
        "updated_at": time.time(),
    }
    save_job(job)
    return job


def save_job(job: dict) -> None:
    job["updated_at"] = time.time()
    with _lock:
        _jobs[job["id"]] = job
        _job_json_path(job["id"]).write_text(json.dumps(job, indent=2))


def get_job(job_id: str) -> dict | None:
    with _lock:
        if job_id in _jobs:
            return _jobs[job_id]
    path = _job_json_path(job_id)
    if path.exists():
        job = json.loads(path.read_text())
        with _lock:
            _jobs[job_id] = job
        return job
    return None


def update_job(job_id: str, **fields) -> dict:
    job = get_job(job_id)
    if job is None:
        raise KeyError(f"job {job_id} not found")
    job.update(fields)
    save_job(job)
    return job


def job_path(job_id: str, *parts: str) -> Path:
    return _job_dir(job_id).joinpath(*parts)


def load_json(job_id: str, filename: str, default=None):
    path = job_path(job_id, filename)
    if not path.exists():
        return default
    return json.loads(path.read_text())


def save_json(job_id: str, filename: str, data) -> None:
    job_path(job_id, filename).write_text(json.dumps(data, indent=2, ensure_ascii=False))


def hydrate_from_disk() -> None:
    if not JOBS_DIR.exists():
        return
    for d in JOBS_DIR.iterdir():
        jp = d / "job.json"
        if jp.exists():
            try:
                job = json.loads(jp.read_text())
                with _lock:
                    _jobs[job["id"]] = job
            except Exception:
                pass
