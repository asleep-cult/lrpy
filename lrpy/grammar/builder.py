from __future__ import annotations

from .exceptions import MissingEntryPointError, UnknownSymbolError
from .grammar import (
    Action,
    Grammar,
    Nonterminal,
    NonterminalSymbol,
    Production,
    Symbol,
    Terminal,
    TerminalSymbol,
)
from ..parser import ast


class GrammarBuilder:
    def __init__(self, node: ast.GrammarNode, tokens: dict[str, int]) -> None:
        self.node = node
        self.tokens = tokens
        self.grammar = Grammar()

        self._groups = 0
        self._optionals = 0
        self._repeats = 0

    def _expand_item(self, item: ast.ItemNode) -> Symbol:
        if isinstance(item, (ast.StringItemNode, ast.IdentifierItemNode)):
            return self._create_symbol(item)

        if isinstance(item, ast.OptionalItemNode):
            return self._create_optional_symbol(item)

        if isinstance(item, ast.RepeatItemNode):
            return self._create_repeat_symbol(item, False)

        if isinstance(item, ast.OptionalRepeatItemNode):
            return self._create_repeat_symbol(item, True)

        if isinstance(item, ast.GroupItemNode):
            return self._create_group_symbol(item)

    def _create_symbol(self, item: ast.ItemNode) -> Symbol:
        if isinstance(item, ast.StringItemNode):
            if item.string not in self.tokens:
                raise UnknownSymbolError(f'Unknown symbol {item.string!r}')

            return TerminalSymbol(string=item.string)

        if isinstance(item, ast.IdentifierItemNode):
            if item.identifier in self.grammar.nonterminals:
                return NonterminalSymbol(name=item.identifier)

            if item.identifier not in self.tokens:
                raise UnknownSymbolError(f'Unknown symbol {item.identifier!r}')

            return TerminalSymbol(string=item.identifier)

        raise TypeError('Expected StringItenNode or IdentifierItemNode')

    def _create_optional_symbol(self, item: ast.ItemNode) -> Symbol:
        if not isinstance(item, ast.OptionalItemNode):
            raise TypeError('Expected OptionalItemNode')

        symbol = self._expand_item(item.item)

        name = f'__Optional{self._optionals}__'
        self._optionals += 1

        nonterminal = Nonterminal(name=name)

        production = Production()
        production.add_symbol(symbol)
        nonterminal.add_production(production)

        production = Production()
        action = Action(body='return None')
        production.set_action(action)
        nonterminal.add_production(production)

        self.grammar.add_nonterminal(nonterminal)

        return NonterminalSymbol(name=name)

    def _create_repeat_symbol(self, item: ast.ItemNode, optional: bool) -> Symbol:
        if not isinstance(item, (ast.RepeatItemNode, ast.OptionalRepeatItemNode)):
            raise TypeError('Expected RepeatItemNode or OptionalRepeatItemNode')

        symbol = self._expand_item(item.item)

        name = f'__Repeat{self._repeats}__'
        self._repeats += 1

        nonterminal = Nonterminal(name=name)

        production = Production()
        production.add_symbol(symbol)

        action = Action(body='return [__symbol__]')
        action.add_name(0, '__symbol__')

        production.set_action(action)
        nonterminal.add_production(production)

        production = Production()
        production.add_symbol(NonterminalSymbol(name=name))
        production.add_symbol(symbol)

        action = Action(body='__symbols__.append(__symbol__); return __symbols__')
        action.add_name(0, '__symbol__')
        action.add_name(1, '__symbols__')

        production.set_action(action)
        nonterminal.add_production(production)

        if optional:
            production = Production()
            action = Action(body='return None')
            production.set_action(action)
            nonterminal.add_production(production)

        self.grammar.add_nonterminal(nonterminal)
        return NonterminalSymbol(name=name)

    def _create_group_symbol(self, item: ast.ItemNode) -> Symbol:
        if not isinstance(item, ast.GroupItemNode):
            return TypeError('Expected GroupItemNode')

        name = f'__Group{self._groups}__'
        self._groups += 1

        nonterminal = Nonterminal(name=name)

        production = Production()
        for item in item.items:
            production.add_symbol(self._expand_item(item))

        self.grammar.add_nonterminal(nonterminal)
        return NonterminalSymbol(name=name)

    def build(self) -> Grammar:
        for string, value in self.tokens.items():
            self.grammar.add_terminal(Terminal(string=string, value=value))

        for rule in self.node.rules:
            if rule.toplevel:
                self.grammar.add_entrypoint(NonterminalSymbol(name=rule.name))

            self.grammar.add_nonterminal(Nonterminal(name=rule.name))

        for rule in self.node.rules:
            nonterminal = self.grammar.nonterminals[rule.name]

            for alternative in rule.alternatives:
                production = Production()

                if alternative.action is not None:
                    action = Action(body=alternative.action)
                else:
                    action = None

                for i, item in enumerate(alternative.items):
                    if isinstance(item, ast.NamedItemNode):
                        if action is not None:
                            action.add_name(i, item.name)

                    production.add_symbol(self._expand_item(item))

                nonterminal.add_production(production)

        if not self.grammar.entrypoints:
            raise MissingEntryPointError(
                'Grammar has no entrypoint. Use \'$\' to denote an entrypoint'
            )

        return self.grammar
