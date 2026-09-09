from abc import ABC, abstractmethod

from captions.models import CaptionEvent, Canvas, StyleParams


class CaptionStyle(ABC):
    id: str
    display_name: str
    needs_anchor: bool = False

    @abstractmethod
    def render(
        self, events: list[CaptionEvent], canvas: Canvas, params: StyleParams
    ) -> tuple[list[str], list[str]]:
        """Returns ([ass style lines], [ass dialogue lines])."""
        raise NotImplementedError
