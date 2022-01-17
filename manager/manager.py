from datetime import datetime
import json
import sys
import traceback
from web3 import Web3

from threading import Thread
from time import sleep
from group.group import Group
from group.router import Router
from group.token.base_token import BaseToken
from group.token.side_token import SideToken
from group.trading_pair import TradingPair


from manager.worker import Worker
from utils.logger import Logger
from utils.utilities import GWEI_1, address0

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
        self.baseTokens = list(map(lambda kw: BaseToken(**kw), model['bases']))
        self.sideTokens = list(map(lambda kw: SideToken(**kw), model['sides']))


        self.refreshRate = refreshRate

        logger = Logger(open("logs.txt", "a"), 0)
        logger = Logger(sys.__stdout__, 1, logger)
        self.logger = Logger(open("orders.txt", "a"), 2, logger)


        self.worker = Worker(self.account, abi, self.web3, self.logger, self.exchangeOracle, self.executor,
                             self.routers, self.baseTokens, self.sideTokens)

    @staticmethod
    def generateState(abi, model, network):
        web3 = Web3(Web3.HTTPProvider(model['provider']))
        groups = []
        
        for baseToken in model['bases']:
            for sideToken in model['sides']:
                symbol = f"{baseToken['name']}/{sideToken['name']}"
                minAmount = int(sideToken['minAmount'] * 10 ** sideToken['decimals'])
                print(f"------------------------------------------------------------{symbol}------------------------------------------------------------")
                pairs = []
                for router in model['routers']:
                    routerContract = web3.eth.contract(address=router['address'], abi=abi['IUniswapRouter'])
                    factoryAddr = routerContract.functions.factory().call()
                    factoryContract = web3.eth.contract(address=factoryAddr, abi=abi['IUniswapFactory'])
                    pairAddr = factoryContract.functions.getPair(baseToken['address'], sideToken['address']).call()
                    if pairAddr != address0:
                        pairContract = web3.eth.contract(address=pairAddr, abi=abi['IUniswapPair'])
                        token0Addr = pairContract.functions.token0().call()
                        isReversed = token0Addr != baseToken['address']

                        reserveToken0, reserveToken1, _ = pairContract.functions.getReserves().call()
                        if isReversed:
                            reserveToken0, reserveToken1 = reserveToken1, reserveToken0

                        if reserveToken1 > minAmount:
                            print(f"{router['name'].ljust(15)} {symbol.ljust(15)} {pairAddr}   "
                                    f"{'{:.8f}'.format(reserveToken1 / reserveToken0 * 10 ** (baseToken['decimals'] - sideToken['decimals']))} "
                                    f"{'{:.8f}'.format(reserveToken0 / 10 ** baseToken['decimals'])} {'{:.8f}'.format(reserveToken1 / 10 ** sideToken['decimals'])}")
                            pairs.append(TradingPair(pairAddr, router['address'], router['r'], baseToken['address'], sideToken['address'], isReversed))
                if pairs.__len__() > 1:
                    groups.append(Group(minAmount, pairs))
                print()

        groupsJson = []
        for group in groups:
            groupsJson.append(group.toJson())
        state = {
            'provider': model['provider'],
            'exchangOracleAddr': model['exchangOracleAddr'],
            'executorAddr': model['executorAddr'],
            'name': dict(map(lambda x: (x['address'], x['name']), model['sides'] + model['bases'] + model['routers'])),
            'decimals': dict(map(lambda x: (x['address'], x['decimals']), model['sides'] + model['bases'])),
            'groups' : groupsJson
        }

        
        print(json.dumps(state, indent=4))
        f = open(f"state/{network}.json", "w")
        json.dump(state, f, indent=4)
        f.close()

    def start(self):
        Thread(target=self.worker.start, daemon=True).start()

        sideTokensAddrs = list(map(lambda sideToken: sideToken.address, self.sideTokens))
        while True:
            try:
                ethBalance, sideTokensBalance = self.exchangeOracle.functions.getAccountBalance(sideTokensAddrs, self.account['address']).call()
                msg = f"STATUS\n"
                for (sideToken, balance) in zip(self.sideTokens, sideTokensBalance):
                    msg += f"{sideToken.name.ljust(7)}: {'{:.4f}'.format(balance / 10 ** sideToken.decimals)}\n"
                msg += f"{'ETH'.ljust(7)}: {'{:.4f}'.format(ethBalance / 10 ** 18)}\n"
                msg += f"Time {datetime.now().strftime('%d-%m-%Y at %H:%M:%S')}\n"
                self.logger.write(msg, 1)
                sleep(self.refreshRate)
            except KeyboardInterrupt:
                self.logger.write("Interrupt by User!", 1)
                self.logger.close()
                return
            except Exception as e:
                    self.logger.write(f"EXCEPTION in {self.__class__.__name__}: {e}!", 1)
                    self.logger.write(traceback.format_exc(), 0)
