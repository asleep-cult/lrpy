import enum

from ..bases import BaseToken
from ..textspan import TextSpan


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
    DOLLAR = enum.auto()
    ARROW = enum.auto()


class Token(BaseToken):
    __slots__ = ()

    def __init__(self, type: TokenType, span: TextSpan) -> None:
        super().__init__(type, span)


class ForeignBlockToken(Token):
    __slots__ = ('content',)

    def __init__(self, span: TextSpan, content: str) -> None:
        super().__init__(TokenType.FOREIGNBLOCK, span)
        self.content = content


class StringToken(BaseToken):
    __slots__ = ('content',)

    def __init__(self, span: TextSpan, content: str) -> None:
        super().__init__(TokenType.STRING, span)
        self.content = content

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} content={self.content!r} {self.span!r}>'


class IdentifierToken(BaseToken):
    __slots__ = ('content',)

    def __init__(self, span: TextSpan, content: str) -> None:
        super().__init__(TokenType.IDENTIFIER, span)
        self.content = content

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} content={self.content!r} {self.span!r}>'
