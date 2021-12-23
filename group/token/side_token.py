from group.token.token import Token


class SideToken(Token):
    def __init__(self, minAmount, **kwargs) -> None:
        super().__init__(**kwargs)
        self.minAmount = minAmount
        self.balance = 0
    
    def setBalance(self, balance: int):
        self.balance = balance
