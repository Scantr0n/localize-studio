from captions.ass_writer import dlg
from captions.colors import COLORS, CYCLE
from captions.models import CaptionEvent, Canvas, StyleParams
from captions.styles.base import CaptionStyle

# Reference canvas this style's proportions were tuned against (tonight's
# 1080x1920 Şengün video). Font sizes/margins/anchor default all scale off
# this ratio so the style still looks right at other resolutions.
REF_W, REF_H = 1080, 1920
REF_BASE_FONT = 120
REF_TAG_FONT = 66
REF_BASE_OUTLINE = 8
REF_TAG_OUTLINE = 4
REF_MARGIN_V = 200
REF_MARGIN_LR = 25
REF_ANCHOR = (760, 650)


class HeadTagStyle(CaptionStyle):
    id = "head_tag"
    display_name = "Head Tag (big color-cycling caption + name/greeting tag near face)"
    needs_anchor = True

    def render(self, events: list[CaptionEvent], canvas: Canvas, params: StyleParams):
        scale_h = canvas.height / REF_H
        scale_w = canvas.width / REF_W

        base_font = round(REF_BASE_FONT * scale_h)
        tag_font = round(REF_TAG_FONT * scale_h)
        base_outline = round(REF_BASE_OUTLINE * scale_h, 1)
        tag_outline = round(REF_TAG_OUTLINE * scale_h, 1)
        margin_v = round(REF_MARGIN_V * scale_h)
        margin_lr = round(REF_MARGIN_LR * scale_w)

        styles = [
            f"Style: Base,{params.font},{base_font},&H00FFFFFF,&H000000FF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,{base_outline},0,2,{margin_lr},{margin_lr},{margin_v},1",
            f"Style: Tag,{params.font},{tag_font},&H00FFFFFF,&H000000FF,&H004111CE,&H00000000,1,0,0,0,100,100,0,0,1,{tag_outline},0,5,0,0,0,1",
        ]

        palette = params.palette or CYCLE
        anchor = params.anchor or {
            "x": round(REF_ANCHOR[0] * scale_w),
            "y": round(REF_ANCHOR[1] * scale_h),
        }

        out = []
        main_idx = 0
        for ev in events:
            if ev.kind == "tag":
                tag = (
                    "{\\pos(%d,%d)\\frz-9\\fad(120,120)\\fscx65\\fscy65"
                    "\\t(0,160,\\fscx100\\fscy100)}" % (anchor["x"], anchor["y"])
                )
                out.append(dlg(1, ev.start, ev.end, "Tag", tag + ev.text))
            else:
                color_name = palette[main_idx % len(palette)]
                color = COLORS.get(color_name, color_name if color_name.startswith("&H") else COLORS["white"])
                pop = (
                    "{\\c%s\\fscx60\\fscy60\\t(0,160,\\fscx122\\fscy122)"
                    "\\t(160,260,\\fscx100\\fscy100)}" % color
                )
                out.append(dlg(0, ev.start, ev.end, "Base", pop + ev.text))
                main_idx += 1
        return styles, out
