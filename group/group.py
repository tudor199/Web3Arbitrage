from math import sqrt
from typing import Tuple
from group.trading_pair import TradingPair


def getInputPrice(amountIn, reserveIn, reserveOut, r):
    amountInWithFee = amountIn * r
    numerator = amountInWithFee * reserveOut
    denominator = reserveIn + amountInWithFee
    return int(numerator / denominator)

def getVirtualReserves(RA0, RA1, RB0, RB1, ra, rb):
    return (
        (RA0 * RB1) / (RB1 + RA1 * rb),
        (rb * RA1 * RB0) / (RB1 + RA1 * rb)
    )

def bestIaDeriv(RA0, RA1, RB0, RB1, ra, rb):
    E0, E1 = getVirtualReserves(RA0, RA1, RB0, RB1, ra, rb)
    inputAmount = int((sqrt(E0 * E1 * ra) - E0) / ra)
    # return (inputAmount, getInputPrice(inputAmount, E0, E1, ra)) if inputAmount > 0 else (0,0)
    return (inputAmount, getInputPrice(getInputPrice(inputAmount, RA0, RA1, ra), RB1, RB0, rb)) if inputAmount > 0 else (0,0)

class Group:
    def __init__(self, sideToken, minAmount: int, pairs: list, name: dict={}, decimals: dict={}) -> None:
        self.sideToken = sideToken
        self.minAmount = minAmount
        self.pairs = list(map(lambda pairJson: TradingPair(**pairJson), pairs))
        self.noPairs = len(pairs)
        self.name = name
        self.decimals = decimals
    
    def toJson(self):
        pairsJson = []
        for pair in self.pairs:
            pairsJson.append(pair.toJson())

        return {
            "sideToken": self.pairs[0].sideToken,
            "minAmount": self.minAmount,
            "pairs": pairsJson
        }


    def computeOrder(self, reservesToken0, reservesToken1) -> Tuple[int, int, TradingPair, TradingPair]:
        for i in range(self.noPairs):
            if self.pairs[i].isReversed:
                rtBaseI, rtSideI = reservesToken1[i], reservesToken0[i]
            else:
                rtBaseI, rtSideI = reservesToken0[i], reservesToken1[i]

            symbol = f"{self.name[self.pairs[i].baseToken]}_{self.name[self.pairs[i].sideToken]}"
            print(f"{self.name[self.pairs[i].router].ljust(15)} {symbol.ljust(15)}   "
                  f"{'{:.8f}'.format(rtSideI / rtBaseI * 10 ** (self.decimals[self.pairs[i].baseToken] - self.decimals[self.pairs[i].sideToken]))}   "
                  f"{'{:.8f}'.format(rtBaseI / 10 ** self.decimals[self.pairs[i].baseToken])} {'{:.8f}'.format(rtSideI / 10 ** self.decimals[self.pairs[i].sideToken])}")
                         
        for i in range(self.noPairs):
            for j in range(self.noPairs):
                if i != j:
                    if self.pairs[i].isReversed:
                        rtBaseI, rtSideI = reservesToken1[i], reservesToken0[i]
                    else:
                        rtBaseI, rtSideI = reservesToken0[i], reservesToken1[i]

                    if self.pairs[j].isReversed:
                        rtBaseJ, rtSideJ = reservesToken1[j], reservesToken0[j]
                    else:
                        rtBaseJ, rtSideJ = reservesToken0[j], reservesToken1[j]

                    amountIn, amountOut = bestIaDeriv(rtSideI, rtBaseI, rtSideJ, rtBaseJ, self.pairs[i].r, self.pairs[j].r)

                    if amountIn > 0:
                        return (amountIn, amountOut, self.pairs[i], self.pairs[j])
        return None