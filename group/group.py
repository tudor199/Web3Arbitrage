from group.trading_pair import TradingPair


ETHER_1 = 10 ** 18

def getInputPrice(input_amount: int, input_reserve: int, output_reserve: int, feeNumerator) -> int:
    numerator = input_amount * feeNumerator * output_reserve
    denominator = input_reserve * 10000 + input_amount * feeNumerator
    return numerator // denominator

class Group:
    def __init__(self, pairs) -> None:
        self.pairs = pairs
        self.noPairs = len(pairs)

    @staticmethod
    def bestIaSearch(rtBaseBuy, rtSideBuy, feeNumeratorBuy, rtBaseSell, rtSideSell, feeNumeratorSell, decimals):
        if rtSideBuy / rtBaseBuy >= rtSideSell / rtBaseSell:
            return 0, 0

        UNIT_1 = 10 ** decimals
        left = int(0.01 * UNIT_1)
        right = int(1000 * UNIT_1)
        while right - left > 0.1 * UNIT_1:
            mid = (left + right) // 2
            profit = getInputPrice(getInputPrice(mid, rtSideBuy, rtBaseBuy, feeNumeratorBuy), rtBaseSell, rtSideSell,feeNumeratorSell) - mid
            midRight = int(mid * 1.01)
            profitRight = getInputPrice(getInputPrice(midRight, rtSideBuy, rtBaseBuy, feeNumeratorBuy), rtBaseSell, rtSideSell, feeNumeratorSell) - midRight
            # print(left // UNIT_1, right // UNIT_1, mid // UNIT_1, profit // UNIT_1)
            if profit < profitRight:
                left = midRight
            else:
                right = mid
        if profit > 0:
            return mid, mid + profit
        return 0, 0

    def computeOrder(self, reservesToken0, reservesToken1):
        for i in range(self.noPairs):
            if self.pairs[i].isReversed:
                rtBaseI, rtSideI = reservesToken1[i], reservesToken0[i]
            else:
                rtBaseI, rtSideI = reservesToken0[i], reservesToken1[i]

            symbol = f"{self.pairs[i].baseToken.name}_{self.pairs[i].sideToken.name}"
            print(f"{self.pairs[i].router.name.ljust(15)} {symbol.ljust(15)}   "
                  f"{'{:.8f}'.format(rtSideI / rtBaseI * 10 ** (self.pairs[i].baseToken.decimals - self.pairs[i].sideToken.decimals))}   "
                  f"{'{:.8f}'.format(rtBaseI / 10 ** self.pairs[i].baseToken.decimals)} {'{:.8f}'.format(rtSideI / 10 ** self.pairs[i].sideToken.decimals)}")
                         
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
                    amountIn, amountOut = Group.bestIaSearch(rtBasej, rtSidej, self.pairs[i].router.feeNumerator,
                                                             rtBasej, rtSidej, self.pairs[j].router.feeNumerator,
                                                             self.pairs[i].sideToken.decimals)

                    # print(amountIn // ETHER_1, amountOut // ETHER_1)
                    if amountIn > 0:
                        return (amountIn, self.pairs[i], self.pairs[j])
        return None