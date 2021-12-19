from __future__ import annotations

from typing import Callable


class EOFType(str):
    def __new__(cls):
        return str.__new__(cls, '\0')

    def __repr__(self):
        return '<EOF>'


EOF = EOFType()


class StringReader:
    def __init__(self, source: str) -> None:
        self.source = source
        self._position = 0

    def at_eof(self) -> bool:
        return self._position >= len(self.source)

    def tell(self) -> int:
        return self._position

    def advance(self, amount: int = 1) -> None:
        self._position += amount

    def peek(self, offset: int = 0) -> str:
        try:
            return self.source[self._position + offset]
        except IndexError:
            return EOF

    def goto(self, string: str) -> bool:
        try:
            index = self.source.index(string, self._position)
        except ValueError:
            return False

        self._position = index + len(string)
        return True

    def goto_eof(self):
        self._position = len(self.source)

    def lookahead(self, func: Callable[[str], bool], *, advance: bool = True) -> bool:
        if not func(self.peek()):
            return False

        if advance:
            self.advance()

        return True

    def skip(self, func: Callable[[str], bool]) -> None:
        while func(self.peek()):
            self.advance()

    def skip_whitespace(self, *, linebreaks: bool = False) -> None:
        if linebreaks:
            self.skip(lambda c: is_whitespace(c) or is_linebreak(c))
        else:
            self.skip(is_whitespace)

    def accumulate(self, func: Callable[[str], bool]) -> str:
        startpos = self.tell()
        while func(self.peek()):
            self.advance()

        endpos = self.tell()
        return self.source[startpos:endpos]


def is_whitespace(char: str) -> bool:
    return char in ' \t\f'


def is_linebreak(char: str) -> bool:
    return char in '\r\n'


def is_escape(char: str) -> bool:
    return char == '\\'


def is_identifier_start(char: str) -> bool:
    return (
        'a' <= char <= 'z'
        or 'A' <= char <= 'Z'
        or char == '_'
        or char >= '\x80'
    )


def is_identifier(char: str) -> bool:
    return (
        'a' <= char <= 'z'
        or 'A' <= char <= 'Z'
        or '0' <= char <= '9'
        or char == '_'
        or char >= '\x80'
    )


def is_digit(char: str) -> bool:
    return '0' <= char <= '9'


def is_hexadecimal(char: str) -> bool:
    return (
        'a' <= char <= 'f'
        or 'A' <= char <= 'F'
        or '0' <= char <= '9'
    )


def is_octal(char: str) -> bool:
    return '0' <= char <= '7'


def is_binary(char: str) -> bool:
    return char in '01'
