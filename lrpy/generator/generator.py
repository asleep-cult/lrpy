from __future__ import annotations

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

    def __hash__(self):
        return hash((self.production, self.position))

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

    def is_nonterminal(self):
        return isinstance(self.symbol, NonterminalSymbol)

    def advance(self) -> LRItem:
        return self.__class__(self.production, self.position + 1)


class LRGenerator:
    __slots__ = ('grammar', 'states', 'entrypoints', 'shifts', 'reductions')

    def __init__(self, grammar: Grammar) -> None:
        self.grammar = grammar

        self.states = {}
        self.entrypoints = {}
        self.shifts = []
        self.reductions = []

    def items(self, symbol: NonterminalSymbol) -> frozenset[LRItem]:
        nonterminal = self.grammar.nonterminals[symbol.name]
        return frozenset(LRItem(production, 0) for production in nonterminal.productions)

    def closure(self, items: Iterable[LRItem]) -> frozenset[LRItem]:
        closure = set(items)
        stack = [item for item in items if item.is_nonterminal()]

        while stack:
            for item in self.items(stack.pop().symbol):
                if item not in closure:
                    closure.add(item)

                    if item.is_nonterminal():
                        stack.append(item)

        return frozenset(closure)

    def transitions(self, items: Iterable[LRItem]) -> dict[TerminalSymbol, frozenset[LRItem]]:
        transitions = {}

        for item in items:
            try:
                items = transitions[item.symbol]
            except KeyError:
                items = transitions[item.symbol] = set()

            items.add(item.advance())

        return {symbol: frozenset(items) for symbol, items in transitions.items()}

    def build_states(self) -> None:
        for entrypoint in self.grammar.entrypoints:
            stateno = self.states.setdefault(self.items(entrypoint), len(self.states))
            self.entrypoints[entrypoint] = stateno

        stack = list(self.states)

        while stack:
            shifts = {}
            reductions = []

            transitions = self.transitions(self.closure(stack.pop()))
            for symbol, items in transitions.items():
                if symbol is not None:
                    shifts[symbol] = self.states.setdefault(items, len(self.states))
                    stack.append(items)
                else:
                    reductions.extend(items)

            self.shifts.append(shifts)
            self.reductions.append(reductions)
