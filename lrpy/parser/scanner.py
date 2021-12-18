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
    is_identifier,
    is_identifier_start,
    is_linebreak,
)
from ..textspan import TextSpan


class GrammarScanner(BaseScanner):
    __slots__ = ('parenstack', 'newline')

    def __init__(self, source: str, *, filename: str = '<string>') -> None:
        super().__init__(source, filename=filename)
        self.parenstack = []
        self.newline = False

    def create_span(self, startpos: int) -> TextSpan:
        return TextSpan(startpos, self.position())

    def scan(self) -> Token:
        reader = self.reader
        while True:
            reader.skip_whitespace()
            if reader.at_eof():
                return Token(TokenType.EOF, self.create_span(self.position()))

            if reader.expect('#'):
                if not reader.skip_expect('\n'):
                    reader.skip_to_eof()

                continue

            char = self.reader.peek()
            startpos = self.position()

            if is_linebreak(char):
                reader.advance()

                if self.newline or self.parenstack:
                    continue

                self.newline = True
                return Token(TokenType.NEWLINE, self.create_span(startpos))

            self.newline = False

            if is_identifier_start(char):
                reader.advance()

                while is_identifier(reader.peek()):
                    reader.advance()

                endpos = self.position()
                content = reader.source[startpos:endpos]
                return IdentifierToken(TextSpan(startpos, endpos), content)

            if char in ('\'' '\"'):
                terminator = char

                reader.advance()
                contentstart = self.position()

                while True:
                    if is_linebreak(reader.peek()):
                        raise InvalidGrammarError(
                            self.fmterror(
                                'Unterminated string literal', self.create_span(startpos)
                            )
                        )

                    if reader.expect('\\'):
                        reader.advance()

                    if reader.expect(terminator):
                        break

                    reader.advance()

                contnentend = self.position() - 1
                content = reader.source[contentstart:contnentend]

                endpos = self.position()
                return StringToken(TextSpan(startpos, endpos), content)

            if char == '{':
                reader.advance()
                contentstart = self.position()

                while True:
                    if reader.at_eof():
                        raise InvalidGrammarError(
                            self.fmterror('Unterminated foreign block', self.create_span(startpos))
                        )

                    if reader.expect('}'):
                        break

                    reader.advance()

                contentend = self.position() - 1
                content = self.reader.source[contentstart:contentend]

                endpos = self.position()
                return ForeignBlockToken(TextSpan(startpos, endpos), content)

            if reader.expect('('):
                self.parenstack.append(TokenType.OPENPAREN)
                return Token(TokenType.OPENPAREN, self.create_span(startpos))

            elif reader.expect(')'):
                if (
                    not self.parenstack
                    or self.parenstack.pop() is not TokenType.OPENPAREN
                ):
                    raise InvalidGrammarError(
                        self.fmterror('Unmatched closing parenthesis', self.create_span(startpos))
                    )

                return Token(TokenType.CLOSEPAREN, self.create_span(startpos))

            elif reader.expect('['):
                self.parenstack.append(TokenType.OPENBRACKET)
                return Token(TokenType.OPENBRACKET, self.create_span(startpos))

            elif reader.expect(']'):
                if (
                    not self.parenstack
                    or self.parenstack.pop() is not TokenType.OPENBRACKET
                ):
                    raise InvalidGrammarError(
                        self.fmterror('Unmatched closing bracket', self.create_span(startpos))
                    )

                return Token(TokenType.CLOSEBRACKET, self.create_span(startpos))

            elif reader.expect(':'):
                return Token(TokenType.COLON, self.create_span(startpos))

            elif reader.expect('+'):
                return Token(TokenType.PLUS, self.create_span(startpos))

            elif reader.expect('*'):
                return Token(TokenType.STAR, self.create_span(startpos))

            elif reader.expect('$'):
                return Token(TokenType.DOLLAR, self.create_span(startpos))

            elif reader.expect('='):
                if reader.expect('>'):
                    return Token(TokenType.ARROW, self.create_span(startpos))

            raise InvalidGrammarError(
                self.fmterror('Invalid Token', self.create_span(startpos))
            )
