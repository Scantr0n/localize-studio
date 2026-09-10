import os
import shutil
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
STORAGE_DIR = BACKEND_DIR / "storage"
JOBS_DIR = STORAGE_DIR / "jobs"
JOBS_DIR.mkdir(parents=True, exist_ok=True)

_MAC_FFMPEG = "/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"
_MAC_FFPROBE = "/opt/homebrew/opt/ffmpeg-full/bin/ffprobe"

FFMPEG_BIN = _MAC_FFMPEG if os.path.exists(_MAC_FFMPEG) else (shutil.which("ffmpeg") or "ffmpeg")
FFPROBE_BIN = _MAC_FFPROBE if os.path.exists(_MAC_FFPROBE) else (shutil.which("ffprobe") or "ffprobe")

WHISPER_MODEL = "large-v3"
WHISPER_DEVICE = "cpu"
WHISPER_COMPUTE_TYPE = "int8"

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = "claude-sonnet-4-5"

TARGET_WIDTH = 1080
TARGET_HEIGHT = 1920
