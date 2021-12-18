from __future__ import annotations

import bisect
import io
import re

from .stringreader import StringReader
from .textspan import TextSpan


def padstring(string: str, n: int) -> str:
    return string.ljust(n + len(string))


class BaseToken:
    __slots__ = ('type', 'span')

    def __init__(self, type: int, span: TextSpan) -> None:
        self.type = type
        self.span = span

    @property
    def pos(self) -> int:
        return self.span.startpos

    @property
    def length(self) -> int:
        return self.span.endpos - self.span.startpos

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} type={self.type!r} {self.span!r}>'


class BaseScanner:
    __slots__ = ('filename', 'reader', 'linestarts')

    def __init__(self, source: str, *, filename: str = '<string>') -> None:
        self.filename = filename
        self.reader = StringReader(source)

        self.linestarts = []
        for match in re.finditer('\n', source):
            self.linestarts.append(match.end())

    def __repr__(self) -> str:
        lineno = self.lineno()
        position = self.position()
        return f'<{self.__class__.__name__} lineno={lineno} position={position}>'

    def fmterror(self, message: str, span: TextSpan) -> None:
        lineno = self.lineno(span.startpos)

        startpos = self.linestart(lineno)
        endpos = self.linestart(lineno + 1)

        error = io.StringIO()
        error.writelines((
            f'File {self.filename!r}, line {lineno}: {message}',
            self.reader.source[startpos:endpos],
            padstring('^' * (span.endpos - span.startpos), span.startpos)
        ))

        return error.getvalue()

    def position(self) -> int:
        return self.reader.tell()

    def lineno(self, pos: int) -> int:
        return bisect.bisect(self.linestarts, pos) + 1

    def linestart(self, lineno: int) -> int:
        return self.linestarts[lineno - 1]

    def scan(self) -> BaseToken:
        raise NotImplementedError
