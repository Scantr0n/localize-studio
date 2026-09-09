from captions.ass_writer import dlg
from captions.models import CaptionEvent, Canvas, StyleParams
from captions.styles.base import CaptionStyle

REF_W, REF_H = 1080, 1920
REF_FONT = 62
REF_OUTLINE = 4
REF_MARGIN_V = 230
REF_MARGIN_LR = 60


class BounceRotateStyle(CaptionStyle):
    id = "bounce_rotate"
    display_name = "Bounce Rotate (punchy gold rotate-and-scale entrance)"
    needs_anchor = False

    def render(self, events: list[CaptionEvent], canvas: Canvas, params: StyleParams):
        scale_h = canvas.height / REF_H
        scale_w = canvas.width / REF_W

        font = round(REF_FONT * scale_h)
        outline = round(REF_OUTLINE * scale_h, 1)
        margin_v = round(REF_MARGIN_V * scale_h)
        margin_lr = round(REF_MARGIN_LR * scale_w)

        styles = [
            f"Style: Default,{params.font},{font},&H002CC7FF,&H000000FF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,{outline},0,2,{margin_lr},{margin_lr},{margin_v},1",
        ]

        out = []
        for ev in events:
            tag = (
                "{\\alpha&HFF&\\frz-16\\fscx55\\fscy55"
                "\\t(0,180,\\alpha&H00&\\frz4\\fscx110\\fscy110)"
                "\\t(180,280,\\frz0\\fscx100\\fscy100)}"
            )
            out.append(dlg(0, ev.start, ev.end, "Default", tag + ev.text))
        return styles, out
