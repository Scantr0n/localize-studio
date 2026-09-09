import re
import subprocess
from collections import Counter
from dataclasses import dataclass

from config import FFMPEG_BIN, FFPROBE_BIN


@dataclass
class VideoInfo:
    width: int
    height: int
    duration: float
    fps: float


@dataclass
class CropBox:
    x: int
    y: int
    w: int
    h: int
    auto_detected: bool = True


def probe(path: str) -> VideoInfo:
    out = subprocess.run(
        [
            FFPROBE_BIN, "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=width,height,r_frame_rate",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1",
            path,
        ],
        capture_output=True, text=True, check=True,
    )
    vals = {}
    for line in out.stdout.strip().splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            vals[k] = v
    width = int(vals.get("width", 0))
    height = int(vals.get("height", 0))
    duration = float(vals.get("duration", 0))
    fps_raw = vals.get("r_frame_rate", "30/1")
    try:
        n, d = fps_raw.split("/")
        fps = float(n) / float(d) if float(d) else 30.0
    except Exception:
        fps = 30.0
    return VideoInfo(width=width, height=height, duration=duration, fps=fps)


def detect_crop(path: str, duration: float) -> CropBox:
    sample_points = [p for p in (duration * 0.1, duration * 0.4, duration * 0.7) if p >= 0]
    boxes: list[tuple[int, int, int, int]] = []
    for t in sample_points:
        out = subprocess.run(
            [
                FFMPEG_BIN, "-y", "-ss", str(max(t, 0)), "-i", path,
                "-t", "1.5", "-vf", "cropdetect=24:2:0", "-f", "null", "-",
            ],
            capture_output=True, text=True,
        )
        for m in re.finditer(r"crop=(\d+):(\d+):(\d+):(\d+)", out.stderr):
            boxes.append(tuple(int(g) for g in m.groups()))
    if not boxes:
        info = probe(path)
        return CropBox(x=0, y=0, w=info.width, h=info.height, auto_detected=False)
    most_common = Counter(boxes).most_common(1)[0][0]
    w, h, x, y = most_common
    return CropBox(x=x, y=y, w=w, h=h, auto_detected=True)


def build_crop_scale_filter(crop: CropBox, target_w: int, target_h: int) -> str:
    return f"crop={crop.w}:{crop.h}:{crop.x}:{crop.y},scale={target_w}:{target_h}"


def run_ffmpeg(args: list[str]) -> None:
    cmd = [FFMPEG_BIN, "-y"] + args + ["-loglevel", "error"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {result.stderr[-4000:]}")


def extract_frame(path: str, timestamp: float, out_path: str) -> None:
    run_ffmpeg(["-ss", str(timestamp), "-i", path, "-vframes", "1", out_path])


def extract_audio(path: str, out_path: str) -> None:
    run_ffmpeg(["-i", path, "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", out_path])


def make_working_copy(source_path: str, crop: CropBox, target_w: int, target_h: int, out_path: str) -> None:
    vf = build_crop_scale_filter(crop, target_w, target_h)
    run_ffmpeg(["-i", source_path, "-vf", vf, "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-c:a", "copy", out_path])


def burn_subtitles(source_path: str, ass_path: str, out_path: str) -> None:
    run_ffmpeg(["-i", source_path, "-vf", f"subtitles={ass_path}", "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-c:a", "copy", out_path])
