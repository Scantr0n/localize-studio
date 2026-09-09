from dataclasses import dataclass, field


@dataclass
class CaptionEvent:
    start: float
    end: float
    text: str
    kind: str = "main"  # "main" | "tag"


@dataclass
class Canvas:
    width: int
    height: int


@dataclass
class StyleParams:
    palette: list[str] = field(default_factory=list)
    anchor: dict | None = None  # {"x": int, "y": int}
    font: str = "PingFang SC"
