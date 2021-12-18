from __future__ import annotations

from .exceptions import MissingEntryPointError, UnknownSymbolError
from .grammar import (
    Action,
    Grammar,
    Nonterminal,
    Production,
    Symbol,
    Terminal,
)
from ..parser import ast


class GrammarBuilder:
    def __init__(self, node: ast.GrammarNode, tokens: dict[str, int]):
        self.node = node
        self.tokens = tokens

        self._expansionid = 0
        self._optionalid = 0
        self._repeatid = 0

    def _create_symbol(self, item: ast.ItemNode) -> Symbol:
        if isinstance(item, ast.StringItemNode):
            try:
                token = self.tokens[item.string]
            except KeyError:
                raise UnknownSymbolError(f'Unknown symbol {item.string!r}')
            else:
                return Terminal(token=token)
        elif isinstance(item, ast.IdentifierItemNode):
            try:
                token = self.tokens[item.identifier]
                return Terminal(token=token)
            except KeyError:
                pass

            if item.identifier in self.grammar.nonterminals:
                return Nonterminal(name=item.identifier)

            raise UnknownSymbolError(f'Unknown symbol {item.identifier!r}')

        raise TypeError('Invalid item provided to create_terminal_symbol')

    def _create_expansion_symbol(self, item: ast.ItemNode) -> Symbol:
        if isinstance(item, (ast.StringItemNode, ast.IdentifierItemNode)):
            return self._create_symbol(item)

        elif isinstance(item, ast.OptionalItemNode):
            return self._create_repeat_symbol(item)

        elif isinstance(item, ast.RepeatItemNode):
            return self._create_repeat_symbol(item, optional=False)

        elif isinstance(item, ast.OptionalRepeatItemNode):
            return self._create_repeat_symbol(item, optional=True)

        elif isinstance(item, ast.GroupItemNode):
            symbols = []

            for item in item.items:
                symbols.append(self._create_expansion_symbol(item))

            name = f'@Expansion{self._expansionid}'
            self._expansionid += 1

            self.grammar.add_nonterminal(
                name=name, productions=[Production(symbols=symbols, action=None)]
            )

            return Nonterminal(name=name)

        raise TypeError('Invalid item provided to create_expansion_symbol')

    def _create_optional_symbol(self, item: ast.ItemNode) -> Symbol:
        expansion = self._create_expansion_symbol(item.item)

        name = f'@Optional{self._optionalid}'
        self._optionalid += 1

        self.grammar.add_nonterminal(
            name=name,
            productions=[
                Production(
                    symbols=[expansion], action=None
                ),
                Production(
                    symbols=[], action=Action(names=[], body='return None')
                )
            ]
        )

        return Nonterminal(name=name)

    def _create_repeat_symbol(self, item: ast.ItemNode, *, optional: bool) -> Symbol:
        expansion = self._create_expansion_symbol(item.item)

        name = f'@Repeat{self._repeatid}'
        self._repeatid += 1

        productions = [
            Production(
                symbols=[expansion],
                action=Action(names=[(0, 'symbol')], body='return [symbol]')
            ),
            Production(
                symbols=[Nonterminal(name=name), expansion],
                action=Action(
                    names=[(0, 'symbols'), (1, 'symbol')],
                    body='symbols.append(symbol); return symbols'
                )
            )
        ]

        if optional:
            productions.append(
                Production(
                    symbols=[],
                    action=Action(names=[], body='return None')
                )
            )

        self.grammar.add_nonterminal(name=name, productions=productions)

        return Nonterminal(name=name)

    def _create_production(self, alternative: ast.AlternativeNode) -> Production:
        names = []
        symbols = []

        for i, item in enumerate(alternative.items):
            if isinstance(item, ast.NamedItemNode):
                names.append((i, item.name))
                item = item.item

            symbols.append(self._create_expansion_symbol(item))

        return Production(symbols=symbols, action=Action(names=names, body=alternative.action))

    def build(self) -> Grammar:
        self.grammar = Grammar()

        for key, value in self.tokens.items():
            self.grammar.add_terminal(string=key, value=value)

        for rule in self.node.rules:
            if rule.toplevel:
                self.grammar.add_entrypoint(name=rule.name)

            self.grammar.add_nonterminal(name=rule.name, productions=[])

        for rule in self.node.rules:
            nonterminal = self.grammar.nonterminals[rule.name]

            for alternative in rule.alternatives:
                nonterminal.productions.append(self._create_production(alternative))

        if not self.grammar.entrypoints:
            raise MissingEntryPointError(
                'Grammar has no entrypoint. Use "$" to denote a top level rule.'
            )

        return self.grammar
