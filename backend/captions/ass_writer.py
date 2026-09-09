import re

# NOTE: PingFang SC is macOS-bundled; a cross-platform port would need a
# fallback font list here.

HEADER_TMPL = """[Script Info]
ScriptType: v4.00+
PlayResX: {w}
PlayResY: {h}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
{styles}

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def ts(t: float) -> str:
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h:d}:{m:02d}:{s:05.2f}"


def dlg(layer: int, start: float, end: float, style: str, text: str) -> str:
    return f"Dialogue: {layer},{ts(start)},{ts(end)},{style},,0,0,0,,{text}"


def has_cjk(text: str) -> bool:
    return bool(re.search(r"[一-鿿]", text))


def est_width(text: str, fontsize: float) -> float:
    n = 0.0
    for ch in text:
        if ch in ("\\", "N"):
            continue
        n += fontsize * (1.0 if has_cjk(ch) else 0.56)
    return n


def widest_line(text: str, fontsize: float) -> float:
    lines = text.split("\\N")
    return max(est_width(l, fontsize) for l in lines)


def line_count(text: str) -> int:
    return text.count("\\N") + 1


def rounded_rect(w: float, h: float, r: float) -> str:
    k = round(0.5523 * r, 1)
    return (
        f"m {r} 0 l {w-r} 0 b {w-r+k} 0 {w} {r-k} {w} {r} "
        f"l {w} {h-r} b {w} {h-r+k} {w-r+k} {h} {w-r} {h} "
        f"l {r} {h} b {r-k} {h} 0 {h-r+k} 0 {h-r} "
        f"l 0 {r} b 0 {r-k} {r-k} 0 {r} 0"
    )


def render_ass(width: int, height: int, style_lines: list[str], dialogue_lines: list[str]) -> str:
    return HEADER_TMPL.format(w=width, h=height, styles="\n".join(style_lines)) + "\n".join(dialogue_lines) + "\n"
