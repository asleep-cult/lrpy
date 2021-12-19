from __future__ import annotations

from typing import Iterable, Optional

from ..grammar.grammar import (
    Grammar,
    NonterminalSymbol,
    Production,
    Symbol,
)


class LRItem:
    __slots__ = ('production', 'position')

    def __init__(self, production: Production, position: int) -> None:
        self.production = production
        self.position = position

    def __repr__(self) -> str:
        return f'Item(production={self.production!r}, position={self.position})'

    def __eq__(self, other: LRItem) -> bool:
        if not isinstance(other, LRItem):
            return NotImplemented

        return (
            self.production == other.production
            and self.position == other.position
        )

    @property
    def reducible(self) -> bool:
        return self.position == len(self.production.symbols)

    @property
    def shiftable(self) -> bool:
        return self.position <= len(self.production.symbols)

    @property
    def symbol(self) -> Optional[Symbol]:
        if not self.reducible:
            return self.production.symbols[self.position]

    def advance(self):
        return self.__class__(self.production, self.position + 1)


class LRState:
    __slots__ = ('stateno', 'items', 'reductions', 'shifts', 'gotos')

    def __init__(self, stateno: int, items: list[LRItem]) -> None:
        self.stateno = stateno
        self.items = items
        self.shifts: dict[str, int] = {}
        self.gotos: dict[str, int] = {}
        self.reductions = []

    def __repr__(self) -> str:
        return f'LRState(stateno={self.stateno}, items={self.items!r})'

    def __eq__(self, other):
        if not isinstance(other, LRState):
            return NotImplemented

        return self.items == other.items


class LRGenerator:
    __slots__ = ('grammar', 'ntstates')

    def __init__(self, grammar: Grammar) -> None:
        self.grammar = grammar

    def closure(self, items: Iterable[LRItem]) -> list[LRItem]:
        stack = list(items)
        closure = []

        while stack:
            item = stack.pop()
            if isinstance(item.symbol, NonterminalSymbol):
                symbol = self.grammar.nonterminals[item.symbol.name]

                for production in symbol.productions:
                    item = LRItem(production, 0)

                    if item not in closure:
                        stack.append(item)
                        closure.append(item)
            else:
                closure.append(item)

        return closure

    def items(self, nonterminal) -> list[LRItem]:
        return [LRItem(production, 0) for production in nonterminal.productions]

    def generate(self) -> list[LRState]:
        states = []

        for entrypoint in self.grammar.entrypoints:
            stack = []

            symbol = self.grammar.nonterminals[entrypoint]
            stack.append(self.items(symbol))

            while stack:
                items = self.closure(stack.pop())
                state = LRState(len(states), items)

                for item in items:
                    if item.reducible:
                        state.reductions.append(item.production)
                    else:
                        stack.append([item.advance()])

                        if isinstance(item.symbol, NonterminalSymbol):
                            state.gotos[item.symbol.name] = len(states) + 1
                        else:
                            state.shifts[item.symbol.string] = len(states) + 1

                states.append(state)

            return states
