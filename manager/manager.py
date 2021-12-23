import sys
import traceback
from web3 import Web3

from threading import Thread
from time import sleep
from group.router import Router
from group.token.base_token import BaseToken
from group.token.side_token import SideToken


from manager.worker import Worker
from utils.logger import Logger
from utils.utilities import GWEI_1

from web3.middleware import geth_poa_middleware


class Manager:
    def __init__(self, account: dict, abi: dict, model: dict, refreshRate: int=600) -> None:
        self.account = account
        self.abi = abi

        self.web3 = Web3(Web3.HTTPProvider(model['provider']))
        self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        self.exchangeOracle = self.web3.eth.contract(address=model['exchangOracleAddr'], abi=self.abi['IExchangeOracle'])
        self.executor = self.web3.eth.contract(address=model['executorAddr'], abi=self.abi['IExchangeOracle'])

        self.routers = list(map(lambda kw: Router(**kw), model['routers']))
        self.bases = list(map(lambda kw: BaseToken(**kw), model['bases']))
        self.sides = list(map(lambda kw: SideToken(**kw), model['sides']))


        self.refreshRate = refreshRate

        logger = Logger(open("logs.txt", "a"), 0)
        logger = Logger(sys.__stdout__, 1, logger)
        self.logger = Logger(open("orders.txt", "a"), 2, logger)


        self.worker = Worker(self.account, abi, self.web3, self.logger, self.exchangeOracle, self.executor,
                             self.routers, self.bases, self.sides)


    def start(self):
        Thread(target=self.worker.start, daemon=True).start()
        while True:
            try:
                sleep(self.refreshRate)
                print("Hearth bit!")
            except KeyboardInterrupt:
                self.logger.write("Interrupt by User!", 1)
                self.logger.close()
                return
            except Exception as e:
                    self.logger.write(f"EXCEPTION in {self.__class__.__name__}: {e}!", 1)
                    self.logger.write(traceback.format_exc(), 0)
