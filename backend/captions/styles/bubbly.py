from captions.ass_writer import dlg
from captions.colors import COLORS, CYCLE
from captions.models import CaptionEvent, Canvas, StyleParams
from captions.styles.base import CaptionStyle

REF_W, REF_H = 1080, 1920
REF_FONT = 60
REF_OUTLINE = 3
REF_MARGIN_V = 230
REF_MARGIN_LR = 60

POP = "\\fscx65\\fscy65\\t(0,150,\\fscx106\\fscy106)\\t(150,230,\\fscx100\\fscy100)"


class BubblyStyle(CaptionStyle):
    id = "bubbly"
    display_name = "Bubbly (playful color-cycling pop-in)"
    needs_anchor = False

    def render(self, events: list[CaptionEvent], canvas: Canvas, params: StyleParams):
        scale_h = canvas.height / REF_H
        scale_w = canvas.width / REF_W

        font = round(REF_FONT * scale_h)
        outline = round(REF_OUTLINE * scale_h, 1)
        margin_v = round(REF_MARGIN_V * scale_h)
        margin_lr = round(REF_MARGIN_LR * scale_w)

        styles = [
            f"Style: Default,{params.font},{font},&H00FFFFFF,&H000000FF,&H00FFFFFF,&H00000000,1,0,0,0,100,100,0,0,1,{outline},0,2,{margin_lr},{margin_lr},{margin_v},1",
        ]

        palette = params.palette or CYCLE
        out = []
        for i, ev in enumerate(events):
            color_name = palette[i % len(palette)]
            color = COLORS.get(color_name, color_name if color_name.startswith("&H") else COLORS["white"])
            tag = "{\\c%s%s}" % (color, POP)
            out.append(dlg(0, ev.start, ev.end, "Default", tag + ev.text))
        return styles, out
