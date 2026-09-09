from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

import jobs
from pipeline.translate import TranslationError, translate_segments

router = APIRouter()


class TranslateRequest(BaseModel):
    target_lang: str


def _do_translate(job_id: str, target_lang: str):
    try:
        segments = jobs.load_json(job_id, "transcript.json", default=[])
        result = translate_segments(segments, target_lang)
        translations = jobs.load_json(job_id, "translations.json", default={})
        translations[target_lang] = {str(k): v for k, v in result.items()}
        jobs.save_json(job_id, "translations.json", translations)
        jobs.update_job(job_id, status="translated", progress=1.0)
    except TranslationError as e:
        jobs.update_job(job_id, status="error", error=str(e))
    except Exception as e:
        jobs.update_job(job_id, status="error", error=str(e))


@router.post("/api/jobs/{job_id}/translate")
async def translate_endpoint(job_id: str, req: TranslateRequest, background: BackgroundTasks):
    job = jobs.get_job(job_id)
    if job is None:
        raise HTTPException(404, "job not found")
    if not jobs.load_json(job_id, "transcript.json"):
        raise HTTPException(400, "no transcript yet")
    jobs.update_job(job_id, status="translating", progress=0.0)
    background.add_task(_do_translate, job_id, req.target_lang)
    return {"status": "translating"}


@router.get("/api/jobs/{job_id}/translations")
async def get_translations(job_id: str):
    return jobs.load_json(job_id, "translations.json", default={})


class TranslationUpdate(BaseModel):
    translations: dict[str, str]  # segment_id (str) -> text


@router.patch("/api/jobs/{job_id}/translations/{lang}")
async def update_translations(job_id: str, lang: str, req: TranslationUpdate):
    job = jobs.get_job(job_id)
    if job is None:
        raise HTTPException(404, "job not found")
    translations = jobs.load_json(job_id, "translations.json", default={})
    translations.setdefault(lang, {}).update(req.translations)
    jobs.save_json(job_id, "translations.json", translations)
    return translations[lang]
