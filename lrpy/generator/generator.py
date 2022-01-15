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
    def symbol(self) -> Optional[Symbol]:
        if len(self.production.symbols) > self.position:
            return self.production.symbols[self.position]

    def is_nonterminal(self):
        return isinstance(self.symbol, NonterminalSymbol)

    def advance(self) -> LRItem:
        return self.__class__(self.production, self.position + 1)


class LRGenerator:
    __slots__ = (
        'grammar',
        'states',
        'entrypoints',
        'shifts',
        'reductions',
        'empty',
        'first',
        'follow',
    )

    def __init__(self, grammar: Grammar) -> None:
        self.grammar = grammar

        self.states = {}
        self.entrypoints = {}
        self.shifts = []
        self.reductions = []

        self.empty = self.calculate_empty()
        self.first = self.calculate_first()
        # self.follow = self.calculate_follow()

    def calculate_empty(self):
        symbols = set()
        for nonterminal in self.grammar.nonterminals.values():
            if not all(production.symbols for production in nonterminal.productions):
                symbols.add(NonterminalSymbol(name=nonterminal.name))

        while True:
            changed = False

            for nonterminal in self.grammar.nonterminals.values():
                if any(
                    symbols.issuperset(production.symbols) for production in nonterminal.productions
                ):
                    symbol = NonterminalSymbol(name=nonterminal.name)
                    if symbol not in symbols:
                        symbols.add(NonterminalSymbol(name=nonterminal.name))
                        changed = True

            if not changed:
                return symbols

    def calculate_first(self):
        symbols = {}
        for terminal in self.grammar.terminals.values():
            symbol = TerminalSymbol(string=terminal.string)
            symbols[symbol] = {symbol}

        for nonterminal in self.grammar.nonterminals.values():
            first = set()
            for production in nonterminal.productions:
                for symbol in production.symbols:
                    first.add(symbol)
                    if symbol not in self.empty:
                        break

            symbol = NonterminalSymbol(name=nonterminal.name)
            symbols[symbol] = first

        while True:
            changed = False

            for symbol, first in symbols.items():
                length = len(first)
                for sym in tuple(first):
                    symbols[symbol].update(symbols[sym])

                if len(first) > length:
                    changed = True

            if not changed:
                return symbols

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
            self.entrypoints[entrypoint] = self.states.setdefault(
                self.items(entrypoint), len(self.states)
            )

        stack = list(self.states)

        while stack:
            transitions = self.transitions(self.closure(stack.pop(0)))

            shifts = {}
            reductions = []

            for symbol, items in transitions.items():
                if symbol is not None:
                    try:
                        stateno = self.states[items]
                    except KeyError:
                        stateno = self.states[items] = len(self.states)
                        stack.append(items)

                    shifts[symbol] = stateno
                else:
                    reductions.extend(items)

            self.shifts.append(shifts)
            self.reductions.append(reductions)
