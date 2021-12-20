from __future__ import annotations

from collections import defaultdict
from typing import Iterable, Optional

from ..grammar.grammar import (
    Grammar,
    NonterminalSymbol,
    Production,
    Symbol,
    TerminalSymbol,
)


class LRItem:
    __slots__ = ('production', 'position')

    def __init__(self, production: Production, position: int) -> None:
        self.production = production
        self.position = position

    def __eq__(self, other: LRItem) -> bool:
        if not isinstance(other, LRItem):
            return NotImplemented

        return (
            self.production == other.production
            and self.position == other.position
        )

    def __repr__(self) -> str:
        return f'LRItem(production={self.production!r}, position={self.position!r})'

    @property
    def reducible(self) -> bool:
        return self.position == len(self.production.symbols)

    @property
    def symbol(self) -> Optional[Symbol]:
        if not self.reducible:
            return self.production.symbols[self.position]

    def advance(self) -> LRItem:
        return self.__class__(self.production, self.position + 1)


class LRState:
    __slots__ = ('index', 'items', 'reductions', 'shifts', 'gotos')

    def __init__(self, index: int, items: list[LRItem]) -> None:
        self.index = index
        self.items = items

        self.shifts: dict[str, str] = {}
        self.gotos: dict[str, str] = {}
        self.reductions: list[Production] = []

    def add_shift(self, symbol: TerminalSymbol, index: int) -> None:
        self.shifts[symbol.string] = index

    def add_goto(self, symbol: NonterminalSymbol, index: int) -> None:
        self.gotos[symbol.name] = index

    def add_reduction(self, production: Production) -> None:
        self.reductions.append(production)


class LRGenerator:
    __slots__ = ('grammar',)

    def __init__(self, grammar: Grammar) -> None:
        self.grammar = grammar

    def items(self, symbol: NonterminalSymbol) -> list[LRItem]:
        items = []

        nonterminal = self.grammar.nonterminals[symbol.name]
        for production in nonterminal.productions:
            items.append(LRItem(production, 0))

        return items

    def closure(self, items: Iterable[LRItem]) -> list[LRItem]:
        stack = list(items)
        closure = list(items)

        while stack:
            item = stack.pop()
            if not isinstance(item.symbol, NonterminalSymbol):
                continue

            for item in self.items(item.symbol):
                if item not in closure:
                    closure.append(item)
                    stack.append(item)

        return closure

    def generate(self) -> list[LRState]:
        stack = []
        states = []
        index = 0

        for entrypoint in self.grammar.entrypoints:
            stack.append((index, self.items(entrypoint)))
            index += 1

        while stack:
            idx, items = stack.pop()
            items = self.closure(items)
            state = LRState(idx, items)

            transitions = defaultdict(list)

            for item in items:
                if item.reducible:
                    state.add_reduction(item.production)
                else:
                    shifts = transitions[item.symbol]
                    shifts.append(item.advance())

            for symbol, shifts in transitions.items():
                if isinstance(symbol, NonterminalSymbol):
                    state.add_goto(symbol, index)
                else:
                    state.add_shift(symbol, index)

                stack.append((index, shifts))
                index += 1

            states.append(state)

        return states
