from captions.styles.bounce_rotate import BounceRotateStyle
from captions.styles.bubbly import BubblyStyle
from captions.styles.comic_pop import ComicPopStyle
from captions.styles.head_tag import HeadTagStyle

STYLE_REGISTRY = {
    HeadTagStyle.id: HeadTagStyle(),
    BubblyStyle.id: BubblyStyle(),
    BounceRotateStyle.id: BounceRotateStyle(),
    ComicPopStyle.id: ComicPopStyle(),
}
