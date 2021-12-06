from __future__ import annotations

from typing import TypeVar

T = TypeVar('T', bound='TextSpan')


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

    def copy(self: T) -> T:
        return self.__class__(self.startpos, self.endpos)

    def extend(self, other: TextSpan) -> TextSpan:
        if not isinstance(other, TextSpan):
            raise TypeError(f'Expected TextSpan, got {other.__class__.__name__}')

        if other.startpos < self.startpos:
            startpos = other.startpos
        else:
            startpos = self.startpos

        if other.endpos > self.endpos:
            endpos = other.endpos
        else:
            endpos = self.endpos

        return self.__class__(startpos, endpos)

    def overlaps(self, other: TextSpan) -> bool:
        if not isinstance(other, TextSpan):
            return TypeError(f'Expected TextSpan, got {other.__class__.__name__}')

        return (
            other.startpos > self.startpos
            and other.endpos < self.endpos
        )
