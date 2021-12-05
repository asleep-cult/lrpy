from __future__ import annotations

import enum
from typing import Optional, Union


class Grammar:
    def __init__(self) -> None:
        self.terminals: dict[str, TerminalDef] = {}
        self.nonterminals: dict[str, NonterminalDef] = {}

    def add_terminal(self, *, type: TerminalType, string: str) -> None:
        self.terminals[string] = TerminalDef(type=type, string=string)

    def add_nonterminal(self, *, name: str, productions: list[Production]) -> None:
        self.nonterminals[name] = NonterminalDef(name=name, productions=productions)

    def __repr__(self) -> str:
        return f'<Grammar terminals={self.terminals!r}, nonterminal={self.nonterminals!r}>'


class Terminal:
    __slots__ = ('token',)

    def __init__(self, *, token: int) -> None:
        self.token = token

    def __repr__(self) -> str:
        return f'Terminal(token={self.token})'


class Nonterminal:
    __slots__ = ('name',)

    def __init__(self, *, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:
        return f'Nonterminal(name={self.name!r})'


Symbol = Union[Terminal, Nonterminal]


class Action:
    __slots__ = ('names', 'body')

    def __init__(self, *, names: list[tuple[int, str]], body: str) -> None:
        self.names = names
        self.body = body

    def __repr__(self) -> str:
        return f'Action(names={self.names!r}, body={self.body!r})'


class Production:
    __slots__ = ('symbols', 'action')

    def __init__(self, *, symbols: list[Symbol], action: Optional[Action]) -> None:
        self.symbols = symbols
        self.action = action

    def __repr__(self) -> str:
        return f'Production(symbols={self.symbols}, action={self.action!r})'


class NonterminalDef:
    __slots__ = ('name', 'productions')

    def __init__(self, name: str, productions: list[Production]) -> None:
        self.name = name
        self.productions = productions

    def __repr__(self) -> str:
        return f'NonterminalDef(name={self.name!r}, productions={self.productions!r})'


class TerminalType(enum.IntEnum):
    IDENTIFIER = enum.auto()
    STRING = enum.auto()


class TerminalDef:
    __slots__ = ('type', 'string')

    def __init__(self, *, type: TerminalType, string: str) -> None:
        self.type = type
        self.string = string

    def __repr__(self) -> str:
        return f'TerminalDef(type={self.type!r}, string={self.string!r})'
