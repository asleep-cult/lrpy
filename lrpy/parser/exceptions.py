class InvalidEncodingDeclarationError(Exception):
    pass


class InvalidGrammarError(Exception):
    __slots__ = ('message',)

    def __init__(self, message: str) -> None:
        self.message = message

    def __repr__(self) -> str:
        return f'\n{self.message}'
