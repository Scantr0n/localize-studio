import json
import re

import anthropic

from config import ANTHROPIC_API_KEY, ANTHROPIC_MODEL

LANG_NAMES = {
    "zh": "Simplified Chinese, phrased the way native Chinese social media (Weibo/Xiaohongshu/Douyin) captions actually read — natural and native-feeling, not a literal/stiff translation",
    "en": "English, natural and conversational",
    "tr": "Turkish, natural and conversational",
    "ja": "Japanese, natural and conversational",
    "ko": "Korean, natural and conversational",
}


class TranslationError(Exception):
    pass


def translate_segments(segments: list[dict], target_lang: str) -> dict[int, str]:
    if not ANTHROPIC_API_KEY:
        raise TranslationError(
            "No ANTHROPIC_API_KEY found. Add one to backend/.env to use AI translation."
        )
    lang_desc = LANG_NAMES.get(target_lang, target_lang)
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    payload = [{"id": s["id"], "text": s["text"]} for s in segments]
    prompt = (
        f"Translate each line below into {lang_desc}.\n"
        "You're given the full clip's lines in order for context, but translate each "
        "line independently as its own caption. Keep translations short enough to work "
        "as a video caption. Preserve names as commonly rendered in the target language "
        "when that's more natural than a literal transliteration.\n\n"
        f"Lines (JSON): {json.dumps(payload, ensure_ascii=False)}\n\n"
        "Respond with ONLY a JSON array like "
        '[{"id": 0, "translation": "..."}, ...] and nothing else.'
    )

    resp = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = resp.content[0].text.strip()
    match = re.search(r"\[.*\]", raw, re.DOTALL)
    if not match:
        raise TranslationError(f"Could not parse translation response: {raw[:500]}")
    parsed = json.loads(match.group(0))
    return {item["id"]: item["translation"] for item in parsed}
