import json
from textwrap import indent
import traceback
from typing import List
from web3 import Web3
from web3.contract import Contract
from datetime import datetime
from time import sleep

from group.group import Group
from group.token.base_token import BaseToken
from group.token.side_token import SideToken
from group.trading_pair import TradingPair
from utils.logger import Logger
from utils.utilities import address0

class Worker:
    def __init__(self, account: dict, abi: dict, web3: Web3, logger: Logger, sideTokens: list, groupsJson: list,
                 exchangeOracle: Contract, executor: Contract, name: dict={}, decimals: dict={}) -> None:
        self.account = account
        self.abi = abi
        self.web3 = web3
        self.logger = logger
        self.sideTokens = sideTokens
        self.groups = list(map(lambda groupJson: Group(**groupJson, name=name, decimals=decimals), groupsJson))
        self.exchangeOracle = exchangeOracle
        self.executor = executor
        self.name = name
        self.decimals = decimals

    def start(self):
        offsets = [0]
        tradingPairAddrs = []
        for group in self.groups:
            offsets.append(offsets[-1] + group.noPairs)
            tradingPairAddrs += list(map(lambda pair: pair.address, group.pairs))
        
        ethBalance = None
        sideTokensBalance = None
        while True:
            try:
                if ethBalance is None:
                    ethBalance, tokensBalance = self.exchangeOracle.functions.getAccountBalance(self.sideTokens, self.account['address']).call()
                    sideTokensBalance = dict(zip(self.sideTokens, tokensBalance))
                
                print(f"--------------------------{datetime.now()}----------------------------")
                reservesToken0, reservesToken1 = self.exchangeOracle.functions.getExchangesState(tradingPairAddrs).call()
                for (i, group) in enumerate(self.groups):
                    order = group.computeOrder(reservesToken0[offsets[i] : offsets[i + 1]], reservesToken1[offsets[i] : offsets[i + 1]])
                    if order:
                        print(f"FOUND: {order}")
                        quit()
                    print()
                sleep(1)

            except Exception as e:
                self.logger.write(f"EXCEPTION in {self.__class__.__name__}: {e}!", 1)
                self.logger.write(traceback.format_exc(), 0)