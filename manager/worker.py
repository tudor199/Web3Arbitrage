import traceback
from web3 import Web3
from web3.contract import Contract
from datetime import datetime
from time import sleep

from group.group import Group
from utils.logger import Logger

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
        
        arbitrageGasRequired = 300_000
        while True:
            try:
                reservesToken0, reservesToken1 = self.exchangeOracle.functions.getExchangesState(tradingPairAddrs).call()
                for (i, group) in enumerate(self.groups):
                    order = group.computeOrder(reservesToken0[offsets[i] : offsets[i + 1]], reservesToken1[offsets[i] : offsets[i + 1]])
                    if order:
                        amountIn, amountOut, pairBuy, pairSell = order
                        if amountOut - amountIn > group.minAmount:
                            tx = self.executor.functions.execute(amountIn, group.minAmount,
                                                                 pairBuy.address, int(pairBuy.r * 10000),
                                                                 pairSell.address, int(pairSell.r * 10000),
                                                                 pairBuy.sideToken, pairBuy.baseToken
                            ).buildTransaction({
                                'gas': arbitrageGasRequired,
                                'gasPrice': self.web3.eth.gasPrice * 2,
                                'from': self.account['address'],
                                'nonce': self.web3.eth.getTransactionCount(self.account['address'])
                            })
                            
                            # Revert check
                            self.web3.eth.estimateGas(tx)

                            print(self.web3.eth.gasPrice * 2)

                            signedTransaction = self.web3.eth.account.signTransaction(tx, private_key=self.account['privateKey'])
                            self.web3.eth.sendRawTransaction(signedTransaction.rawTransaction)
                            txHash = signedTransaction['hash'].hex()
                            self.logger.write(f"Transaction submited with txHash: {txHash}", 2)
                            while True:
                                sleep(1)
                                receipt = self.web3.eth.waitForTransactionReceipt(txHash)
                                if receipt:
                                    self.logger.write(f"asdasd : {'SUCCESS' if receipt['status'] == 1 else 'REVERT' }", 2)
                                    for key in receipt:
                                        self.logger.write(f"{key}: {receipt[key]}", 1)
                                    break
                sleep(1)

            except Exception as e:
                self.logger.write(f"EXCEPTION in {self.__class__.__name__}: {e}!", 1)
                self.logger.write(traceback.format_exc(), 0)