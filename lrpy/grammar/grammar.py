from __future__ import annotations

from typing import Optional, Union


class Grammar:
    __slots__ = ('entrypoints', 'terminals', 'nonterminals')

    def __init__(self) -> None:
        self.entrypoints: list[str] = []
        self.terminals: dict[str, Terminal] = {}
        self.nonterminals: dict[str, Nonterminal] = {}

    def __repr__(self) -> str:
        return (
            f'Grammar(entrypoints={self.entrypoints!r}, '
            f'terminals={self.terminals!r}, nonterminals={self.nonterminals!r})'
        )

    def add_entrypoint(self, entrypoint: str) -> None:
        self.entrypoints.append(entrypoint)

    def add_terminal(self, terminal: Terminal) -> None:
        self.terminals[terminal.string] = terminal

    def add_nonterminal(self, nonterminal: Nonterminal) -> None:
        self.nonterminals[nonterminal.name] = nonterminal


class Nonterminal:
    __slots__ = ('name', 'productions')

    def __init__(self, *, name: str) -> None:
        self.name = name
        self.productions = []

    def __repr__(self) -> str:
        return f'Nonterminal(name={self.name!r}, productions={self.productions!r})'

    def add_production(self, production: Production) -> None:
        production.set_nonterminal(self.name)
        self.productions.append(production)


class Terminal:
    __slots__ = ('string', 'value')

    def __init__(self, *, string: str, value: int) -> None:
        self.string = string
        self.value = value

    def __repr__(self) -> str:
        return f'Terminal(string={self.string!r}, value={self.value!r})'


class NonterminalSymbol:
    __slots__ = ('name',)

    def __init__(self, *, name: str) -> None:
        self.name = name

    def __eq__(self, other: NonterminalSymbol) -> bool:
        if not isinstance(other, NonterminalSymbol):
            return NotImplemented

        return self.name == other.name

    def __repr__(self) -> str:
        return f'NonterminalSymbol(name={self.name!r})'


class TerminalSymbol:
    __slots__ = ('string',)

    def __init__(self, *, string: str) -> None:
        self.string = string

    def __eq__(self, other: TerminalSymbol) -> bool:
        if not isinstance(other, TerminalSymbol):
            return NotImplemented

        return self.string == other.string

    def __repr__(self) -> str:
        return f'TerminalSymbol(string={self.string!r})'


class Action:
    __slots__ = ('names', 'body')

    def __init__(self, *, body: str) -> None:
        self.names: list[tuple[int, str]] = []
        self.body = body

    def __repr__(self) -> str:
        return f'Action(names={self.names!r}, body={self.body!r})'

    def add_name(self, index: int, name: str) -> None:
        self.names.append((index, name))


class Production:
    __slots__ = ('nonterminal', 'symbols', 'action')

    def __init__(self) -> None:
        self.nonterminal: Optional[str] = None
        self.symbols: list[Symbol] = []
        self.action: Optional[Action] = None

    def __repr__(self) -> str:
        return (
            f'Production(nonterminal={self.nonterminal}, '
            f'symbols={self.symbols}, action={self.action})'
        )

    def set_nonterminal(self, nonterminal: str) -> None:
        self.nonterminal = nonterminal

    def set_action(self, action: Action) -> None:
        self.action = action

    def add_symbol(self, symbol: Symbol) -> None:
        self.symbols.append(symbol)


Symbol = Union[TerminalSymbol, NonterminalSymbol]
