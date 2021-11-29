import io

from . import ast
from .exceptions import InvalidGrammarError
from .scanner import GrammarScanner
from .tokens import Token, TokenType


class GrammarParser:
    __slots__ = ('source', 'scanner', 'tokens')

    def __init__(self, source: io.TextIOBase) -> None:
        self.source = source
        self.scanner = GrammarScanner(source)
        self.tokens = []

    def fail(self, msg: str, token: Token):
        self.source.seek(self.scanner.linestarts[token.range.startlineno - 1])
        line = (
            self.source.readline().strip('\n') + '\n' + (' ' * token.range.startpos)
            + '    ' + ('^' * (token.range.endpos - token.range.startpos))
        )

        name = getattr(self.source, 'name', '<unknown>')
        raise InvalidGrammarError(
            f'\nFile {name!r}, line {token.range.startlineno}: {msg}'
            f'\n    {line}'
        )

    def peek_token(self) -> Token:
        try:
            token = self.tokens[0]
        except IndexError:
            token = self.scanner.scan()
            self.tokens.append(token)

        return token

    def consume_token(self) -> Token:
        try:
            return self.tokens.pop(0)
        except IndexError:
            return self.scanner.scan()

    def skip_newlines(self) -> None:
        while True:
            token = self.peek_token()
            if token.type is TokenType.NEWLINE:
                self.consume_token()
            else:
                break

    def _parse_rule(self) -> ast.RuleNode:
        rule_token = self.consume_token()
        if (
            rule_token.type is not TokenType.IDENTIFIER
            or rule_token.content != 'rule'
        ):
            self.fail('Expected "rule"', rule_token)

        name_token = self.consume_token()
        if name_token.type is not TokenType.IDENTIFIER:
            self.fail('Expected identifier', name_token)

        colon_token = self.consume_token()
        if colon_token.type is not TokenType.COLON:
            self.fail('Expected colon', colon_token)

        alternatives = []
        alternative = self._parse_alternative()
        range = rule_token.range.extend(alternative.range)

        alternatives.append(alternative)

        while True:
            self.skip_newlines()

            token = self.peek_token()
            if token.type is TokenType.OPENPAREN:
                alternative = self._parse_alternative()
                range = range.extend(alternative.range)
                alternatives.append(alternative)
            else:
                break

        return ast.RuleNode(range=range, name=name_token.content, alternatives=alternatives)

    def _parse_alternative(self) -> ast.AlternativeNode:
        self.skip_newlines()

        openparen_token = self.consume_token()
        if openparen_token.type is not TokenType.OPENPAREN:
            self.fail('Expected open parenthesis', openparen_token)

        items = []
        item = self._parse_item()
        range = openparen_token.range.extend(item.range)

        items.append(item)

        while True:
            token = self.peek_token()
            if token.type is TokenType.CLOSEPAREN:
                self.consume_token()
                range = range.extend(token.range)

                break

            items.append(self._parse_item())

        token = self.peek_token()
        if token.type is TokenType.ARROW:
            self.consume_token()
            token = self.consume_token()
            if token.type is not TokenType.FOREIGNBLOCK:
                self.fail('Expected block', token)

            range = range.extend(token.range)
            action = token.block
        else:
            action = None

        return ast.AlternativeNode(range, items=items, action=action)

    def _parse_item(self) -> ast.ItemNode:
        token = self.consume_token()
        if token.type is TokenType.OPENBRACKET:
            item = self._parse_item()

            closebracket_token = self.consume_token()
            if closebracket_token.type is not TokenType.CLOSEBRACKET:
                self.fail('Expected close bracket', closebracket_token)

            item = ast.OptionalItemNode(
                token.range.extend(item.range).extend(closebracket_token.range), item=item
            )

        elif token.type is TokenType.STRING:
            item = ast.StringItemNode(token.range, string=token.content)

        elif token.type is TokenType.IDENTIFIER:
            colon_token = self.peek_token()
            if colon_token.type is TokenType.COLON:
                self.consume_token()
                item = self._parse_item()
                return ast.NamedItemNode(
                    token.range.extend(item.range), name=token.content, item=item
                )
            else:
                item = ast.IdentifierItemNode(token.range, identifier=token.content)

        elif token.type is TokenType.OPENPAREN:
            items = []
            item = self._parse_item()
            range = token.range.extend(item.range)

            items.append(item)

            while True:
                token = self.peek_token()
                if token.type is TokenType.CLOSEPAREN:
                    self.consume_token()
                    range = range.extend(token.range)
                    break

                items.append(self._parse_item())

            return ast.GroupItemNode(range, items=items)

        else:
            self.fail('Unexpected Token', token)

        while True:
            token = self.peek_token()
            if token.type is TokenType.PLUS:
                item = ast.RepeatItemNode(item.range.extend(token.range), item=item)
            elif token.type is TokenType.STAR:
                item = ast.OptionalItemNode(item.range.extend(token.range), item=item)
            else:
                break

            self.consume_token()

        return item

    def parse(self) -> ast.GrammarNode:
        rules = []
        start_token = self.peek_token()
        while True:
            token = self.peek_token()
            if token.type is TokenType.EOF:
                break

            rules.append(self._parse_rule())

        return ast.GrammarNode(start_token.range.extend(token.range), rules=rules)
