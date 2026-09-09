from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

import jobs
from routers import prepare, render, transcribe_router, translate_router, upload, jobs_status

app = FastAPI(title="Localize Studio")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(prepare.router)
app.include_router(transcribe_router.router)
app.include_router(translate_router.router)
app.include_router(render.router)
app.include_router(jobs_status.router)


@app.on_event("startup")
async def startup():
    jobs.hydrate_from_disk()


@app.get("/api/health")
async def health():
    return {"ok": True}
