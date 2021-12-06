from __future__ import annotations

from typing import Iterable, Optional

from ..bases import TokenEnum
from ..grammar.grammar import (
    Grammar,
    Nonterminal,
    Production,
    Symbol,
    Terminal,
)


class LRItem:
    __slots__ = ('production', 'position')

    def __init__(self, production: Production, position: int) -> None:
        self.production = production
        self.position = position

    def __repr__(self) -> str:
        return f'Item(production={self.production!r}, position={self.position})'


class LRState:
    __slots__ = ('position', 'items')

    def __init__(self, position: int, items: set[LRItem]) -> None:
        self.position = position
        self.items = items

    def __repr__(self) -> str:
        return f'State(position={self.position!r}, items={self.items!r})'


class LRGenerator:
    __slots__ = ('grammar', 'first_table')

    def __init__(self, grammar: Grammar) -> None:
        self.grammar = grammar

        self.first_table = {}

        updated = True
        while updated:
            for nonterminal in grammar.nonterminals.values():
                for production in nonterminal.productions:
                    tokens = self.first(production.symbols)
                    try:
                        first = self.first_table[nonterminal.name]
                    except KeyError:
                        first = set()
                        self.first_table[nonterminal.name] = first

                    if len(first) != len(tokens):
                        first.update(tokens)
                        updated = True

            updated = False

    def first(
        self, symbols: Iterable[Symbol], *, lookahead: Optional[TokenEnum] = None
    ) -> set[TokenEnum]:
        # Returns a set of all the terminals some symbols can start with
        terminals = set()

        for symbol in symbols:
            if isinstance(symbol, Terminal):
                terminals.add(symbol.token)

            elif isinstance(symbol, Nonterminal):
                first = self.first_table.get(symbol.name)
                if first is not None:
                    terminals.update(first)

            else:
                raise TypeError('Expected Symbol')

        return terminals
