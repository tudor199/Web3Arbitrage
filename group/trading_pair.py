class TradingPair:
    def __init__(self, address: str, router: str, r: float, baseToken: str, sideToken: str, isReversed: bool) -> None:
        self.address = address
        self.router = router
        self.r = r
        self.baseToken = baseToken
        self.sideToken = sideToken
        self.isReversed = isReversed
    
    def toJson(self):
        return {
            "address" : self.address,
            "router" : self.router,
            "r" : self.r,
            "baseToken" : self.baseToken,
            "sideToken" : self.sideToken,
            "isReversed" : self.isReversed
        }