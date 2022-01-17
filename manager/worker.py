import traceback
from typing import List
from web3 import Web3
from web3.contract import Contract
from datetime import datetime
from time import sleep

from group.group import Group
from group.router import Router
from group.token.base_token import BaseToken
from group.token.side_token import SideToken
from group.trading_pair import TradingPair
from utils.logger import Logger
from utils.utilities import address0

class Worker:
    def __init__(self, account: dict, abi: dict, web3: Web3, logger: Logger, exchangeOracle: Contract, executor: Contract,
                 routers: List[Router], bases: List[BaseToken], sides: List[SideToken]) -> None:
        self.account = account
        self.abi = abi
        self.web3 = web3
        self.logger = logger
        self.exchangeOracle = exchangeOracle
        self.executor = executor
        self.routers = routers
        self.baseTokens = bases
        self.sideTokens = sides

    def start(self):
        groups = []
        for baseToken in self.baseTokens:
            for sideToken in self.sideTokens:
                pairs = []
                for router in self.routers:
                    routerContract = self.web3.eth.contract(address=router.address, abi=self.abi['IUniswapRouter'])
                    factoryAddr = routerContract.functions.factory().call()
                    factoryContract = self.web3.eth.contract(address=factoryAddr, abi=self.abi['IUniswapFactory'])
                    symbol = f"{baseToken.name}/{sideToken.name}"
                    pairAddr = factoryContract.functions.getPair(baseToken.address, sideToken.address).call()
                    if pairAddr != address0:
                        pairContract = self.web3.eth.contract(address=pairAddr, abi=self.abi['IUniswapPair'])
                        token0Addr = pairContract.functions.token0().call()
                        isReversed = token0Addr != baseToken.address

                        reserveToken0, reserveToken1, _ = pairContract.functions.getReserves().call()
                        if isReversed:
                            reserveToken0, reserveToken1 = reserveToken1, reserveToken0

                        if reserveToken1 > sideToken.minAmount * 10 ** sideToken.decimals:
                            print(f"{router.name.ljust(15)} {symbol.ljust(15)} {pairAddr}   "
                                    f"{'{:.8f}'.format(reserveToken1 / reserveToken0 * 10 ** (baseToken.decimals - sideToken.decimals))} "
                                    f"{'{:.8f}'.format(reserveToken0 / 10 ** baseToken.decimals)} {'{:.8f}'.format(reserveToken1 / 10 ** sideToken.decimals)}")
                            pairs.append(TradingPair(pairAddr, router, baseToken, sideToken, isReversed))
                if pairs.__len__() > 1:
                    groups.append(Group(pairs))
                print()

        offsets = [0]
        tradingPairAddrs = []
        for group in groups:
            offsets.append(offsets[-1] + group.noPairs)
            tradingPairAddrs += list(map(lambda pair: pair.address, group.pairs))
        
        sideTokensAddrs = list(map(lambda sideToken: sideToken.address, self.sideTokens))
        
        ethBalance = None
        sideTokensBalance = None
        while True:
            try:
                if ethBalance is None:
                    ethBalance, sideTokensBalance = self.exchangeOracle.functions.getAccountBalance(sideTokensAddrs, self.account['address']).call()
                    for (sideToken, balance) in zip(self.sideTokens, sideTokensBalance):
                        sideToken.setBalance(balance)
                    print(ethBalance, sideTokensBalance)
                print(f"--------------------------{datetime.now()}----------------------------")
                reservesToken0, reservesToken1 = self.exchangeOracle.functions.getExchangesState(tradingPairAddrs).call()
                for (i, group) in enumerate(groups):
                    order = group.computeOrder(reservesToken0[offsets[i] : offsets[i + 1]], reservesToken1[offsets[i] : offsets[i + 1]])
                    if order:
                        print(f"FOUND: {order}")
                        quit()
                    print()
                sleep(1)

            except Exception as e:
                self.logger.write(f"EXCEPTION in {self.__class__.__name__}: {e}!", 1)
                self.logger.write(traceback.format_exc(), 0)