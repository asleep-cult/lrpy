from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import Self


class TextSpan:
    def __init__(self, startpos: int, endpos: int) -> None:
        self.startpos = startpos
        self.endpos = endpos

    def __eq__(self, other: TextSpan) -> bool:
        if not isinstance(other, TextSpan):
            return NotImplemented

        return (
            self.startpos == other.startpos
            and self.endpos == other.endpos
        )

    def __repr__(self) -> str:
        return f'{self.startpos}-{self.endpos}'

    def copy(self) -> Self:
        return self.__class__(self.startpos, self.endpos)

    def extend(self, other: TextSpan) -> TextSpan:
        if not isinstance(other, TextSpan):
            raise TypeError(f'Expected TextSpan, got {other.__class__.__name__}')

        startpos = min(self.startpos, other.startpos)
        endpos = max(self.endpos, other.endpos)

        return self.__class__(startpos, endpos)

    def overlaps(self, other: TextSpan) -> bool:
        if not isinstance(other, TextSpan):
            return TypeError(f'Expected TextSpan, got {other.__class__.__name__}')

        return (
            other.startpos > self.startpos
            and other.endpos < self.endpos
        )
