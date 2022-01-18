from math import sqrt
from tokenize import group
from typing import List
from group.trading_pair import TradingPair



def getInputPrice(input_amount: int, input_reserve: int, output_reserve: int, r=99.7/100) -> int:
    numerator = output_reserve * r * input_amount
    denominator = input_reserve + r * input_amount
    return int(numerator // denominator)

def getVirtualReserves(reservesTrxs1, reservesTokens1, reservesTrxs2, reservesTokens2, ra, rb):
    return (
        int((reservesTrxs1 * reservesTokens2) / (reservesTokens2 + reservesTokens1 * rb)),
        int((rb * reservesTokens1 * reservesTrxs2) / (reservesTokens2 + reservesTokens1 * rb))
    )

def bestIaDeriv(reservesTrxs1, reservesTokens1, reservesTrxs2, reservesTokens2, ra, rb):
    E0, E1 = getVirtualReserves(reservesTrxs1, reservesTokens1, reservesTrxs2, reservesTokens2, ra, rb)
    inputAmount = int((sqrt(E0 * E1 * ra) - E0) / ra)
    print(ra, rb)
    print(10000, getInputPrice(10000, E0, E1, ra))
    print(10000, getInputPrice(getInputPrice(10000, reservesTrxs1, reservesTokens1, ra), reservesTokens2, reservesTrxs2, rb))
    return (inputAmount, getInputPrice(inputAmount, E0, E1, ra)) if inputAmount > 0 else (0,0)

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


    def computeOrder(self, reservesToken0, reservesToken1):
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
                    # check his with mock
                    if self.pairs[i].isReversed:
                        rtBaseI, rtSideI = reservesToken1[i], reservesToken0[i]
                    else:
                        rtBaseI, rtSideI = reservesToken0[i], reservesToken1[i]

                    if self.pairs[j].isReversed:
                        rtBasej, rtSidej = reservesToken1[j], reservesToken0[j]
                    else:
                        rtBasej, rtSidej = reservesToken0[j], reservesToken1[j]
                    amountIn, amountOut = bestIaDeriv(rtSidej, rtBasej, rtSidej, rtBasej, self.pairs[i].r, self.pairs[j].r)

                    if amountIn > 0:
                        return (amountIn / 10 ** 18, amountOut / 10 ** 18, self.pairs[i], self.pairs[j])
        return None