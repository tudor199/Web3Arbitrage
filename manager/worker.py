import traceback
from web3 import Web3
from web3.contract import Contract
from datetime import datetime
from time import sleep

from group.group import Group
from utils.logger import Logger

class Worker:
    def __init__(self, account: dict, abi: dict, web3: Web3, logger: Logger, sideTokens: list, gasPrice, groupsJson: list,
                 exchangeOracle: Contract, executor: Contract, name: dict={}, decimals: dict={}) -> None:
        self.account = account
        self.abi = abi
        self.web3 = web3
        self.logger = logger
        self.sideTokens = sideTokens
        self.gasPrice = gasPrice
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
        
        nonce = self.web3.eth.getTransactionCount(self.account['address'])
        arbitrageGasRequired = 300_000
        while True:
            try:
                reservesToken0, reservesToken1 = self.exchangeOracle.functions.getExchangesState(tradingPairAddrs).call()
                for (i, group) in enumerate(self.groups):
                    order = group.computeOrder(reservesToken0[offsets[i] : offsets[i + 1]], reservesToken1[offsets[i] : offsets[i + 1]])
                    if order:
                        amountIn, amountOut, pairBuy, pairSell = order
                        self.logger.write(f"ARBITRAGE_FOUND at {datetime.now().strftime('%d-%m-%Y at %H:%M:%S')}: {self.name[pairBuy.baseToken]}/{self.name[pairBuy.sideToken]} on {self.name[pairBuy.router]} -> {self.name[pairSell.router]}\n"
                                          f"Amounts: {amountIn / 10 ** self.decimals[pairBuy.sideToken]} -> {amountOut / 10 ** self.decimals[pairBuy.sideToken]}\n"
                                          f"Profit: {(amountOut - amountIn) / 10 ** self.decimals[pairBuy.sideToken]} {self.name[pairBuy.sideToken]}", 0)
                        tx = self.executor.functions.execute(amountIn, group.minAmount,
                                                                pairBuy.address, int(pairBuy.r * 10000),
                                                                pairSell.address, int(pairSell.r * 10000),
                                                                pairBuy.sideToken, pairBuy.baseToken
                        ).buildTransaction({
                            'gas': arbitrageGasRequired,
                            'gasPrice': self.gasPrice,
                            'from': self.account['address'],
                            'nonce': nonce
                        })
                        nonce += 1

                        signedTransaction = self.web3.eth.account.signTransaction(tx, private_key=self.account['privateKey'])
                        self.web3.eth.sendRawTransaction(signedTransaction.rawTransaction)
                        txHash = signedTransaction['hash'].hex()
                        self.logger.write(f"TX_SUBMIT at {datetime.now().strftime('%d-%m-%Y at %H:%M:%S')}: {txHash}", 2)
                        while True:
                            sleep(1)
                            receipt = self.web3.eth.waitForTransactionReceipt(txHash)
                            if receipt:
                                self.logger.write(f"EXECUTION at {datetime.now().strftime('%d-%m-%Y at %H:%M:%S')}: {txHash}:  "
                                                f"{self.name[pairBuy.baseToken]}/{self.name[pairBuy.sideToken]} on {self.name[pairBuy.router]} -> {self.name[pairSell.router]} "
                                                f"({(amountOut - amountIn) / 10 ** self.decimals[pairBuy.sideToken]} {self.name[pairBuy.sideToken]}) {'SUCCESS' if receipt['status'] == 1 else 'REVERT' }", 2)
                                
                                self.logger.write(f"TX_DETAILS:", 0)
                                for key in receipt:
                                    self.logger.write(f"{key}: {receipt[key]}", 0)
                                break
                    print()
                print(datetime.now())
                sleep(1)

            except Exception as e:
                self.logger.write(f"EXCEPTION in {self.__class__.__name__}: {e}!", 1)
                self.logger.write(traceback.format_exc(), 0)