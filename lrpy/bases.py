from __future__ import annotations

import io
from typing import Iterable, Optional, TYPE_CHECKING

from .stringreader import StringReader
from .textrange import TextRange


class TokenEnum:
    if TYPE_CHECKING:
        id: int
        name: str
        value: Optional[str]

    def __init_subclass__(cls) -> None:
        cls._tokens_ = {}

        for name, value in cls.__dict__.items():
            if isinstance(value, _TokenWrapper):
                value.initialize(cls, name)

    @classmethod
    def get_token_names(cls) -> Iterable[str]:
        return cls._tokens_.keys()

    @classmethod
    def get_token_values(cls) -> Iterable[TokenEnum]:
        return cls._tokens_.values()

    @classmethod
    def get_token(cls, name: str) -> TokenEnum:
        return cls._tokens_[name]


class _TokenWrapper:
    __slots__ = ('cls', 'id', 'name', 'value')

    def __init__(self, value: Optional[str] = None) -> None:
        self.value = value

    def initialize(self, cls: type[TokenEnum], name: str) -> None:
        self.cls = cls
        self.id = len(cls._tokens_)
        self.name = name
        cls._tokens_[self.name] = self

    def __repr__(self) -> str:
        return f'<{self.cls.__name__}:{self.name}>'


def token(value: Optional[str] = None) -> TokenEnum:
    return _TokenWrapper(value)  # type: ignore


class BaseToken:
    __slots__ = ('type', 'range')

    def __init__(self, type: TokenEnum, range: TextRange) -> None:
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
