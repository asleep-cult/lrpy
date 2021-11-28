from __future__ import annotations

from typing import TypeVar

T = TypeVar('T', bound='TextRange')


class TextRange:
    def __init__(self, startpos: int, endpos: int, startlineno: int, endlineno: int) -> None:
        self.startpos = startpos
        self.endpos = endpos
        self.startlineno = startlineno
        self.endlineno = endlineno

    def __eq__(self, other: TextRange) -> bool:
        if not isinstance(other, TextRange):
            return NotImplemented

        return (
            self.startpos == other.startpos
            and self.endpos == other.endpos
            and self.startlineno == other.startlineno
            and self.endlineno == other.endlineno
        )

    def __repr__(self) -> str:
        if self.startlineno == self.endlineno:
            return f'{self.startlineno}:{self.startpos}:{self.endpos}'
        return f'{self.startlineno}-{self.endlineno}:{self.startpos}:{self.endpos}'

    def copy(self: T) -> T:
        return self.__class__(self.startpos, self.endpos)

    def extend(self: T, other: T) -> T:
        if not isinstance(other, TextRange):
            raise TypeError(f'Expected TextRange, got {other.__class__.__name__}')

        if other.startpos < self.startpos:
            startpos = other.startpos
        else:
            startpos = self.startpos

        if other.endpos > self.endpos:
            endpos = other.endpos
        else:
            endpos = self.endpos

        if other.startlineno < self.startlineno:
            startlineno = other.startlineno
        else:
            startlineno = self.startlineno

        if other.endlineno > self.endlineno:
            endlineno = other.endlineno
        else:
            endlineno = self.endlineno

        return self.__class__(startpos, endpos, startlineno, endlineno)

    def overlaps(self, other: TextRange) -> bool:
        if not isinstance(other, TextRange):
            return TypeError(f'Expected TextRange, got {other.__class__.__name__}')

        return (
            other.startlineno > self.startlineno
            and other.endlineno < self.endlineno
            or other.startpos > self.startpos
            and other.endpos < self.endpos
        )
