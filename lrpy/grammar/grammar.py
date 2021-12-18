from __future__ import annotations

from typing import Optional, Union


class Grammar:
    def __init__(self) -> None:
        self.entrypoints: list[str] = []
        self.terminals: dict[str, TerminalDef] = {}
        self.nonterminals: dict[str, NonterminalDef] = {}

    def add_entrypoint(self, *, name: str) -> None:
        self.entrypoints.append(name)

    def add_terminal(self, *, string: str, value: int) -> None:
        self.terminals[string] = TerminalDef(string=string, value=value)

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

    def __eq__(self, other: Terminal) -> bool:
        if not isinstance(other, Terminal):
            return NotImplemented

        return self.token == other.token


class Nonterminal:
    __slots__ = ('name',)

    def __init__(self, *, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:
        return f'Nonterminal(name={self.name!r})'

    def __eq__(self, other: Nonterminal) -> bool:
        if not isinstance(other, Nonterminal):
            return NotImplemented

        return self.name == other.name


Symbol = Union[Terminal, Nonterminal]


class Action:
    __slots__ = ('names', 'body')

    def __init__(self, *, names: list[tuple[int, str]], body: str) -> None:
        self.names = names
        self.body = body

    def __repr__(self) -> str:
        return f'Action(names={self.names!r}, body={self.body!r})'

    def __eq__(self, other: Action) -> bool:
        if not isinstance(other, Action):
            return NotImplemented

        return (
            self.names == other.names
            and self.body == other.body
        )


class Production:
    __slots__ = ('symbols', 'action')

    def __init__(self, *, symbols: list[Symbol], action: Optional[Action]) -> None:
        self.symbols = symbols
        self.action = action

    def __repr__(self) -> str:
        return f'Production(symbols={self.symbols}, action={self.action!r})'

    def __eq__(self, other: Production) -> bool:
        if not isinstance(other, Production):
            return NotImplemented

        return (
            self.symbols == other.symbols
            and self.action == other.action
        )


class NonterminalDef:
    __slots__ = ('name', 'productions')

    def __init__(self, name: str, productions: list[Production]) -> None:
        self.name = name
        self.productions = productions

    def __repr__(self) -> str:
        return f'NonterminalDef(name={self.name!r}, productions={self.productions!r})'

    def __eq__(self, other: NonterminalDef) -> bool:
        if not isinstance(other, NonterminalDef):
            return NotImplemented

        return (
            self.name == other.name
            and self.productions == other.productions
        )


class TerminalDef:
    __slots__ = ('string', 'value')

    def __init__(self, *, string: str, value: int) -> None:
        self.string = string
        self.value = value

    def __repr__(self) -> str:
        return f'TerminalDef(string={self.string!r}, value={self.value})'

    def __eq__(self, other: TerminalDef) -> bool:
        if not isinstance(other, TerminalDef):
            return NotImplemented

        return (
            self.string == other.string
            and self.value == other.value
        )
