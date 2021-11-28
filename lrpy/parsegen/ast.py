from __future__ import annotations

from typing import Optional, Union

from ..textrange import TextRange


class BaseNode:
    __slots__ = ('range',)

    def __init__(self, range: TextRange) -> None:
        self.range = range


class GrammarNode(BaseNode):
    __slots__ = ('rules',)

    def __init__(self, range: TextRange, *, rules: list[RuleNode]) -> str:
        super().__init__(range)
        self.rules = rules

    def __repr__(self) -> str:
        return f'GrammarNode({self.range!r}, rules={self.rules!r})'

    def __str__(self) -> str:
        return '\n\n'.join(str(rule) for rule in self.rules)


class RuleNode(BaseNode):
    __slots__ = ('name', 'alternatives')

    def __init__(self, range: TextRange, *, name: str, alternatives: list[AlternativeNode]) -> None:
        super().__init__(range)
        self.name = name
        self.alternatives = alternatives

    def __repr__(self) -> str:
        return f'RuleNode({self.range!r}, name={self.name}, alternatives={self.alternatives!r})'

    def __str__(self) -> str:
        parts = [f'rule {self.name} {{']

        for alternative in self.alternatives:
            items = ' '.join(str(item) for item in alternative.items)
            parts.append(f'    ({items}) => {{')
            parts.append(f'        {alternative.action}')
            parts.append('    }\n')

        parts.append('}')

        return '\n'.join(parts)


class AlternativeNode(BaseNode):
    __slots__ = ('items', 'action')

    def __init__(self, range: TextRange, *, items: list[ItemNode], action: Optional[str]) -> None:
        super().__init__(range)
        self.items = items
        self.action = action

    def __repr__(self) -> str:
        return f'AlternativeNode({self.range!r}, items={self.items!r}, action={self.action!r})'

    def __str__(self) -> str:
        items = ' '.join(str(item) for item in self.items)

        parts = [f'({items}) => {{']
        parts.append(f'    {self.action}')
        parts.append('}')

        return '\n'.join(parts)


class NamedItemNode(BaseNode):
    __slots__ = ('name', 'item')

    def __init__(self, range: TextRange, *, name: str, item: ItemNode) -> None:
        super().__init__(range)
        self.name = name
        self.item = item

    def __repr__(self) -> str:
        return f'NamedItemNode({self.range!r}, name={self.name!r}, item={self.item!r})'

    def __str__(self) -> str:
        return f'{self.name}: {self.item}'


class OptionalItemNode(BaseNode):
    __slots__ = ('item',)

    def __init__(self, range: TextRange, *, item: ItemNode) -> None:
        super().__init__(range)
        self.item = item

    def __repr__(self) -> str:
        return f'OptionalItemNode({self.range!r}, item={self.item!r})'

    def __str__(self) -> str:
        return f'[{self.item}]'


class RepeatItemNode(BaseNode):
    __slots__ = ('item',)

    def __init__(self, range: TextRange, *, item: ItemNode) -> None:
        super().__init__(range)
        self.item = item

    def __repr__(self) -> str:
        return f'RepeatItemNode({self.range!r}, item={self.item!r})'

    def __str__(self):
        return f'{self.item}+'


class OptionalRepeatItemNode(BaseNode):
    __slots__ = ('item',)

    def __init__(self, range: TextRange, *, item: ItemNode) -> None:
        super().__init__(range)
        self.item = item

    def __repr__(self) -> str:
        return f'OptionalRepeatItemNode({self.range!r}, item={self.item!r})'

    def __str__(self):
        return f'{self.item}*'


class StringItemNode(BaseNode):
    __slots__ = ('string',)

    def __init__(self, range: TextRange, *, string: str) -> None:
        super().__init__(range)
        self.string = string

    def __repr__(self) -> str:
        return f'StringItemNode({self.range!r}, string={self.string!r})'

    def __str__(self) -> str:
        return f'{self.string!r}'


class IdentifierItemNode(BaseNode):
    __slots__ = ('identifier',)

    def __init__(self, range: TextRange, *, identifier: str) -> None:
        super().__init__(range)
        self.identifier = identifier

    def __repr__(self) -> str:
        return f'IdentifierItemNode({self.range!r}, identifier={self.identifier!r})'

    def __str__(self) -> str:
        return self.identifier


class GroupItemNode(BaseNode):
    __slots__ = ('items',)

    def __init__(self, range: TextRange, *, items: list[ItemNode]) -> None:
        super().__init__(range)
        self.items = items

    def __repr__(self) -> str:
        return f'GroupItemNode({self.range!r}, items={self.items!r})'

    def __str__(self) -> str:
        items = ' '.join(str(item) for item in self.items)
        return f'({items})'


ItemNode = Union[
    NamedItemNode,
    OptionalItemNode,
    RepeatItemNode,
    OptionalRepeatItemNode,
    StringItemNode,
    IdentifierItemNode,
    GroupItemNode,
]
