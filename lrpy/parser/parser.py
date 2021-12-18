from . import ast
from .exceptions import InvalidGrammarError
from .scanner import GrammarScanner
from .tokens import Token, TokenType


class GrammarParser:
    __slots__ = ('source', 'scanner', 'tokens')

    def __init__(self, source: str, *, filename: str = '<string>') -> None:
        self.source = source
        self.scanner = GrammarScanner(source, filename=filename)
        self.tokens = []

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
            raise InvalidGrammarError(
                self.scanner.fmterror('Expected "rule"', rule_token.span)
            )

        dollar_token = self.peek_token()
        if dollar_token.type is TokenType.DOLLAR:
            self.consume_token()
            toplevel = True
        else:
            toplevel = False

        name_token = self.consume_token()
        if name_token.type is not TokenType.IDENTIFIER:
            raise InvalidGrammarError(
                self.scanner.fmterror('Expected identifier', name_token.span)
            )

        colon_token = self.consume_token()
        if colon_token.type is not TokenType.COLON:
            raise InvalidGrammarError(
                self.scanner.fmterror('Expected colon', colon_token.span)
            )

        alternatives = []
        alternative = self._parse_alternative()
        span = rule_token.span.extend(alternative.span)

        alternatives.append(alternative)

        while True:
            self.skip_newlines()

            token = self.peek_token()
            if token.type is TokenType.OPENPAREN:
                alternative = self._parse_alternative()
                span = span.extend(alternative.span)
                alternatives.append(alternative)
            else:
                break

        return ast.RuleNode(
            span=span, toplevel=toplevel, name=name_token.content, alternatives=alternatives
        )

    def _parse_alternative(self) -> ast.AlternativeNode:
        self.skip_newlines()

        openparen_token = self.consume_token()
        if openparen_token.type is not TokenType.OPENPAREN:
            raise InvalidGrammarError(
                self.scanner.fmterror('Expected open parenthesis', openparen_token.span)
            )

        items = []
        item = self._parse_item()
        span = openparen_token.span.extend(item.span)

        items.append(item)

        while True:
            token = self.peek_token()
            if token.type is TokenType.CLOSEPAREN:
                self.consume_token()
                span = span.extend(token.span)

                break

            items.append(self._parse_item())

        token = self.peek_token()
        if token.type is TokenType.ARROW:
            self.consume_token()
            token = self.consume_token()
            if token.type is not TokenType.FOREIGNBLOCK:
                raise InvalidGrammarError(
                    self.scanner.fmterror('Expected block', token.span)
                )

            span = span.extend(token.span)
            action = token.content
        else:
            action = None

        return ast.AlternativeNode(span, items=items, action=action)

    def _parse_item(self, *, named=True) -> ast.ItemNode:
        token = self.consume_token()
        if token.type is TokenType.OPENBRACKET:
            item = self._parse_item(named=False)

            closebracket_token = self.consume_token()
            if closebracket_token.type is not TokenType.CLOSEBRACKET:
                raise InvalidGrammarError(
                    self.scanner.fmterror('Expected close bracket', closebracket_token.span)
                )

            item = ast.OptionalItemNode(
                token.span.extend(closebracket_token.span), item=item
            )

        elif token.type is TokenType.STRING:
            item = ast.StringItemNode(token.span, string=token.content)

        elif token.type is TokenType.IDENTIFIER:
            colon_token = self.peek_token()
            if colon_token.type is TokenType.COLON:
                if not named:
                    raise InvalidGrammarError(
                        self.scanner.fmterror('Named item is not allowed here', token.span)
                    )

                self.consume_token()
                item = self._parse_item(named=False)

                return ast.NamedItemNode(
                    token.span.extend(item.span), name=token.content, item=item
                )
            else:
                item = ast.IdentifierItemNode(token.span, identifier=token.content)

        elif token.type is TokenType.OPENPAREN:
            items = []
            item = self._parse_item(named=False)
            span = token.span.extend(item.span)

            items.append(item)

            while True:
                token = self.peek_token()
                if token.type is TokenType.CLOSEPAREN:
                    self.consume_token()
                    span = span.extend(token.span)
                    break

                items.append(self._parse_item(named=False))

            item = ast.GroupItemNode(span, items=items)

        else:
            raise InvalidGrammarError(
                self.scanner.fmterror('Unexpected Token', token.span)
            )

        token = self.peek_token()
        if token.type is TokenType.PLUS:
            self.consume_token()
            item = ast.RepeatItemNode(item.span.extend(token.span), item=item)

        elif token.type is TokenType.STAR:
            self.consume_token()
            item = ast.OptionalRepeatItemNode(item.span.extend(token.span), item=item)

        return item

    def parse(self) -> ast.GrammarNode:
        rules = []
        start_token = self.peek_token()
        while True:
            token = self.peek_token()
            if token.type is TokenType.EOF:
                break

            rules.append(self._parse_rule())

        return ast.GrammarNode(start_token.span.extend(token.span), rules=rules)
