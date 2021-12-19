from .exceptions import InvalidGrammarError
from .tokens import (
    ForeignBlockToken,
    IdentifierToken,
    StringToken,
    Token,
    TokenType,
)
from ..bases import BaseScanner
from ..stringreader import (
    is_escape,
    is_identifier,
    is_identifier_start,
    is_linebreak,
)


def is_terminator(char: str) -> bool:
    return char == '\'' or char == '\"'


def is_block_start(char: str) -> bool:
    return char == '{'


def is_block_end(char: str) -> bool:
    return char == '}'


class GrammarScanner(BaseScanner):
    __slots__ = ('parenstack', 'bracelevel', 'newline')

    def __init__(self, source: str, *, filename: str = '<string>') -> None:
        super().__init__(source, filename=filename)

        self.parenstack = []
        self.bracelevel = 0
        self.newline = False

    def _scan_identifier(self) -> IdentifierToken:
        assert self.reader.lookahead(is_identifier_start, advance=False)

        startpos = self.position()
        content = self.reader.accumulate(is_identifier)

        return IdentifierToken(self.create_span(startpos), content)

    def _scan_string(self) -> StringToken:
        terminator = self.reader.peek()
        assert self.reader.lookahead(is_terminator)

        contentstart = self.position()
        while True:
            if self.reader.at_eof():
                raise InvalidGrammarError(
                    self.fmterror('Unterminated string literal', self.create_span(contentstart))
                )
            else:
                if self.reader.lookahead(lambda c: c == terminator):
                    break

                if self.reader.lookahead(is_escape):
                    self.reader.advance()

                self.reader.advance()

        contentend = self.position() - 1
        content = self.reader.source[contentstart:contentend]

        return StringToken(self.create_span(contentstart - 1), content)

    def _scan_block(self) -> ForeignBlockToken:
        assert self.reader.lookahead(is_block_start)
        self.bracelevel = 1

        contentstart = self.position()
        while True:
            if self.bracelevel == 0:
                break

            if self.reader.at_eof():
                raise InvalidGrammarError(
                    self.fmterror('Unterminated block', self.create_span(contentstart))
                )
            else:
                if self.reader.lookahead(is_block_start):
                    self.bracelevel += 1
                    continue

                if self.reader.lookahead(is_block_end):
                    self.bracelevel -= 1
                    continue

                self.reader.advance()

        contentend = self.position() - 1
        content = self.reader.source[contentstart:contentend]

        return ForeignBlockToken(self.create_span(contentstart - 1), content)

    def _scan_token(self) -> Token:
        startpos = self.position()

        if self.reader.lookahead(lambda c: c == '('):
            self.parenstack.append(TokenType.OPENPAREN)
            return Token(TokenType.OPENPAREN, self.create_span(startpos))

        if self.reader.lookahead(lambda c: c == ')'):
            if (
                not self.parenstack
                or self.parenstack.pop() is not TokenType.OPENPAREN
            ):
                raise InvalidGrammarError(
                    self.fmterror('Unmatched closing parenthesis', self.create_span(startpos))
                )

            return Token(TokenType.CLOSEPAREN, self.create_span(startpos))

        if self.reader.lookahead(lambda c: c == '['):
            self.parenstack.append(TokenType.OPENBRACKET)
            return Token(TokenType.OPENBRACKET, self.create_span(startpos))

        if self.reader.lookahead(lambda c: c == ']'):
            if (
                not self.parenstack
                or self.parenstack.pop() is not TokenType.OPENBRACKET
            ):
                raise InvalidGrammarError(
                    self.fmterror('Unmatched closing bracket', self.create_span(startpos))
                )

        if self.reader.lookahead(lambda c: c == ':'):
            return Token(TokenType.COLON, self.create_span(startpos))

        if self.reader.lookahead(lambda c: c == '+'):
            return Token(TokenType.PLUS, self.create_span(startpos))

        if self.reader.lookahead(lambda c: c == '*'):
            return Token(TokenType.STAR, self.create_span(startpos))

        if self.reader.lookahead(lambda c: c == '$'):
            return Token(TokenType.DOLLAR, self.create_span(startpos))

        if self.reader.lookahead(lambda c: c == '='):
            if self.reader.lookahead(lambda c: c == '>'):
                return Token(TokenType.ARROW, self.create_span(startpos))

        raise InvalidGrammarError(
            self.fmterror('Invalid Token', self.create_span(startpos))
        )

    def scan(self) -> Token:
        while True:
            self.reader.skip_whitespace()
            if self.reader.at_eof():
                return Token(TokenType.EOF, self.create_span(self.position()))

            if self.reader.lookahead(lambda c: c == '#'):
                if not self.reader.goto('\n'):
                    self.reader.goto_eof()

                continue

            startpos = self.position()

            if self.reader.lookahead(is_linebreak):
                if self.newline or self.parenstack:
                    continue

                self.newline = True
                return Token(TokenType.NEWLINE, self.create_span(startpos))
            else:
                self.newline = False

            if self.reader.lookahead(is_identifier_start, advance=False):
                return self._scan_identifier()

            if self.reader.lookahead(is_terminator, advance=False):
                return self._scan_string()

            if self.reader.lookahead(is_block_start, advance=False):
                return self._scan_block()

            return self._scan_token()
