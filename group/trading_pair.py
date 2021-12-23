from group.router import Router
from group.token.base_token import BaseToken
from group.token.side_token import SideToken


class TradingPair:
    def __init__(self, address: str, router: Router, baseToken: BaseToken, sideToken: SideToken, isReversed: bool) -> None:
        self.address = address
        self.router = router
        self.baseToken = baseToken
        self.sideToken = sideToken
        self.isReversed = isReversed