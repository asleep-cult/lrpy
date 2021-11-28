from __future__ import annotations

import enum
import io
from typing import Optional

from .stringreader import StringReader
from .textrange import TextRange


class BaseToken:
    __slots__ = ('type', 'range')

    def __init__(self, type: enum.Enum, range: TextRange) -> None:
        self.type = type
        self.range = range

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} type={self.type!r} {self.range!r}>'


class BaseScanner:
    __slots__ = ('source', 'linestarts', 'reader')

    def __init__(self, source: io.TextIOBase) -> None:
        self.source = source
        self.linestarts = []
        self.reader: Optional[StringReader] = None

    def __repr__(self) -> str:
        lineno = self.lineno()
        position = self.position()
        return f'<{self.__class__.__name__} {self.source!r} {lineno=} {position=}>'

    def lineno(self) -> int:
        return len(self.linestarts)

    def position(self) -> int:
        if self.reader is None:
            return 0
        else:
            return self.reader.tell()

    def relativepos(self, base: int, lineno: int):
        return self.linestarts[lineno - 1] + base

    def readline(self) -> StringReader:
        self.linestarts.append(self.source.tell())
        self.reader = StringReader(self.source.readline())
        return self.reader

    def scan(self) -> BaseToken:
        raise NotImplementedError
