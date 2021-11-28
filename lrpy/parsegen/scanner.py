import io

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
from ..textrange import TextRange


class GrammarScanner(BaseScanner):
    __slots__ = ('parenstack', 'newline')

    def __init__(self, source: io.TextIOBase) -> None:
        super().__init__(source)
        self.parenstack = []
        self.newline = False

    def create_range(self, startpos: int, endpos: int) -> TextRange:
        lineno = self.lineno()
        return TextRange(startpos, endpos, lineno, lineno)

    def fail(self, msg: str, startpos: int, lineno: int) -> None:
        self.source.seek(self.linestarts[lineno - 1])
        line = self.source.readline().strip('\n') + '\n' + (' ' * startpos) + '    ^'

        name = getattr(self.source, 'name', '<unknown>')
        raise InvalidGrammarError(
            f'\nFile {name!r}, line {lineno}: {msg}'
            f'\n    {line}'
        )

    def scan(self) -> Token:
        if self.reader is None:
            self.readline()

        reader = self.reader
        while True:
            if reader.at_eof():
                if reader.tell() == 0:
                    position = self.position()
                    lineno = self.lineno()
                    return Token(TokenType.EOF, TextRange(position, position, lineno, lineno))

                reader = self.readline()

            reader.skip_whitespace()
            if reader.at_eof():
                continue

            char = reader.peek()
            if char == '-':
                char = reader.peek(1)
                if char == '-':
                    reader.skip_to_eof()
                    continue

            startpos = self.position()
            startlineno = self.lineno()

            if is_linebreak(char):
                reader.advance()

                if self.newline or self.parenstack:
                    continue

                self.newline = True
                return Token(TokenType.NEWLINE, self.create_range(startpos, startpos + 1))

            self.newline = False

            if is_identifier_start(char):
                reader.advance()

                while is_identifier(reader.peek()):
                    reader.advance()

                endpos = self.position()
                content = reader.source[startpos:endpos]
                return IdentifierToken(self.create_range(startpos, endpos), content)

            if char in ('\'' '\"'):
                terminator = char

                reader.advance()
                contentstart = self.position()

                while True:
                    if reader.at_eof():
                        self.fail('Unterminated string literal', startpos, startlineno)

                    char = reader.peek()
                    if char == '\\':
                        reader.advance(2)
                    elif char != terminator:
                        reader.advance(1)
                    else:
                        break

                contnentend = self.position()
                reader.advance()

                content = reader.source[contentstart:contnentend]

                endpos = self.position()
                return StringToken(
                    TextRange(startpos, endpos, startlineno, startlineno), content
                )

            if char == '{':
                reader.advance()
                blockstart = self.position()

                content = io.StringIO()

                while True:
                    if reader.at_eof():
                        if reader.tell() == 0:
                            self.fail('Unterminated Block', startpos, startlineno)

                        content.write(self.reader.source[blockstart:])

                        reader = self.readline()
                        blockstart = 0

                    if reader.expect('}'):
                        if blockstart != 0:
                            content.write(self.reader.source[blockstart:-2])

                        break
                    else:
                        reader.advance()

                endpos = self.position()
                endlineno = self.lineno()
                return ForeignBlockToken(
                    TextRange(startpos, endpos, startlineno, endlineno), content.getvalue()
                )

            if reader.expect('('):
                self.parenstack.append(TokenType.OPENPAREN)
                return Token(TokenType.OPENPAREN, self.create_range(startpos, startpos + 1))

            elif reader.expect(')'):
                if (
                    not self.parenstack
                    or self.parenstack.pop() is not TokenType.OPENPAREN
                ):
                    self.fail('Unmatched closing parenthesis', startpos, startlineno)

                return Token(
                    TokenType.CLOSEPAREN,
                    TextRange(startpos, startpos + 1, startlineno, startlineno)
                )

            elif reader.expect('['):
                self.parenstack.append(TokenType.OPENBRACKET)
                return Token(TokenType.OPENBRACKET, self.create_range(startpos, startpos + 1))

            elif reader.expect(']'):
                if (
                    not self.parenstack
                    or self.parenstack.pop() is not TokenType.OPENBRACKET
                ):
                    self.fail('Unmatched closing bracket', startpos, startlineno)

                return Token(TokenType.CLOSEBRACKET, self.create_range(startpos, startpos + 1))

            elif reader.expect(':'):
                return Token(TokenType.COLON, self.create_range(startpos, startpos + 1))

            elif reader.expect('+'):
                return Token(TokenType.PLUS, self.create_range(startpos, startpos + 1))

            elif reader.expect('*'):
                return Token(TokenType.STAR, self.create_range(startpos, startpos + 1))

            elif reader.expect('='):
                if reader.expect('>'):
                    return Token(TokenType.ARROW, self.create_range(startpos, startpos + 1))

            self.fail('Invalid Token', startpos, startlineno)
