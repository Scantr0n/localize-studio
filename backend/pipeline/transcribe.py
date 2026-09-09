from faster_whisper import WhisperModel

from config import WHISPER_COMPUTE_TYPE, WHISPER_DEVICE, WHISPER_MODEL

_model: WhisperModel | None = None


def get_model() -> WhisperModel:
    global _model
    if _model is None:
        _model = WhisperModel(WHISPER_MODEL, device=WHISPER_DEVICE, compute_type=WHISPER_COMPUTE_TYPE)
    return _model


def transcribe(audio_path: str, language: str | None = None) -> list[dict]:
    model = get_model()
    lang = None if language in (None, "auto") else language
    segments, _info = model.transcribe(
        audio_path,
        task="transcribe",
        language=lang,
        vad_filter=True,
        beam_size=5,
        condition_on_previous_text=False,
    )
    out = []
    for i, seg in enumerate(segments):
        out.append({
            "id": i,
            "start": round(seg.start, 2),
            "end": round(seg.end, 2),
            "text": seg.text.strip(),
        })
    return out
