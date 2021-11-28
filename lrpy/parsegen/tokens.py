import enum

from ..bases import BaseToken
from ..textrange import TextRange


class TokenType(enum.IntEnum):
    FOREIGNBLOCK = enum.auto()
    STRING = enum.auto()
    IDENTIFIER = enum.auto()
    NEWLINE = enum.auto()
    EOF = enum.auto()

    OPENPAREN = enum.auto()
    CLOSEPAREN = enum.auto()

    OPENBRACKET = enum.auto()
    CLOSEBRACKET = enum.auto()

    OPENBRACE = enum.auto()
    CLOSEBRACE = enum.auto()

    COLON = enum.auto()
    PLUS = enum.auto()
    STAR = enum.auto()
    ARROW = enum.auto()


class Token(BaseToken):
    __slots__ = ()

    def __init__(self, type: TokenType, range: TextRange) -> None:
        super().__init__(type, range)


class ForeignBlockToken(Token):
    __slots__ = ('block',)

    def __init__(self, range: TextRange, block: str) -> None:
        super().__init__(TokenType.FOREIGNBLOCK, range)
        self.block = block


class StringToken(BaseToken):
    __slots__ = ('content',)

    def __init__(self, range: TextRange, content: str) -> None:
        super().__init__(TokenType.STRING, range)
        self.content = content

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} content={self.content!r} {self.range!r}>'


class IdentifierToken(BaseToken):
    __slots__ = ('content',)

    def __init__(self, range: TextRange, content: str) -> None:
        super().__init__(TokenType.IDENTIFIER, range)
        self.content = content

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} content={self.content!r} {self.range!r}>'
