from group.token.token import Token


class BaseToken(Token):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)