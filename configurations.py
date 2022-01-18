models = {
    'polygon': {
        # 'provider': 'https://rpc-mainnet.matic.network',
        'provider': 'https://matic-mainnet.chainstacklabs.com',
        
        'exchangOracleAddr': '0x301D28A1f3B833176791Ee8B55cAABcFCA0c1242',
        'executorAddr': '0x53B4d2B88d2a6B16FEed7A8Dd81c249A05799952',
        'routers': [
            {
                'name': 'QuickSwap',
                'address': '0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff',
                'r': 0.9970,
            },
            {
                'name': 'SushiSwap',
                'address': '0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506',
                'r': 0.9970,
            },
            {
                'name': 'ApeSwap',
                'address': '0xC0788A3aD43d79aa53B09c2EaCc313A787d1d607',
                'r': 0.9980,
            },
            {
                'name': 'Polycat',
                'address': '0x94930a328162957FF1dd48900aF67B5439336cBD',
                'r': 0.9975,
            },
            {
                'name': 'Dfyn',
                'address': '0xA102072A4C07F06EC3B4900FDC4C7B80b6c57429',
                'r': 0.9975,
            },
        ],
        'bases': [
            {
                'name': 'QUICK',
                'address': '0x831753DD7087CaC61aB5644b308642cc1c33Dc13',
                'decimals': 18,
            },
            {
                'name': 'AAVE',
                'address': '0xD6DF932A45C0f255f85145f286eA0b292B21C90B',
                'decimals': 18,
            },
            {
                'name': 'SUSHI',
                'address': '0x0b3F868E0BE5597D5DB7fEB59E1CADBb0fdDa50a',
                'decimals': 18,
            },
            {
                'name': 'DFYN',
                'address': '0xC168E40227E4ebD8C1caE80F7a55a4F0e6D66C97',
                'decimals': 18,
            },
            {
                'name': 'BIFI',
                'address': '0xFbdd194376de19a88118e84E279b977f165d01b8',
                'decimals': 18,
            },
            {
                'name': 'AVAX',
                'address': '0x2C89bbc92BD86F8075d1DEcc58C7F4E0107f286b',
                'decimals': 18,
            },
            {
                'name': 'ADDY',
                'address': '0xc3FdbadC7c795EF1D6Ba111e06fF8F16A20Ea539',
                'decimals': 18,
            },
            {
                'name': 'BAL',
                'address': '0x9a71012B13CA4d3D0Cdc72A177DF3ef03b0E76A3',
                'decimals': 18,
            },
            {
                'name': 'LINK',
                'address': '0x53E0bca35eC356BD5ddDFebbD1Fc0fD03FaBad39',
                'decimals': 18,
            },
            {
                'name': 'UNI',
                'address': '0xb33EaAd8d922B1083446DC23f610c2567fB5180f',
                'decimals': 18,
            },
            {
                'name': 'MANA',
                'address': '0xA1c57f48F0Deb89f569dFbE6E2B7f46D33606fD4',
                'decimals': 18,
            },
            {
                'name': 'UST',
                'address': '0x692597b009d13C4049a947CAB2239b7d6517875F',
                'decimals': 18,
            },
            {
                'name': 'CRV',
                'address': '0x172370d5Cd63279eFa6d502DAB29171933a610AF',
                'decimals': 18,
            },
            {
                'name': 'SAND',
                'address': '0xBbba073C31bF03b8ACf7c28EF0738DeCF3695683',
                'decimals': 18,
            },
            {
                'name': 'COMP',
                'address': '0x8505b9d2254A7Ae468c0E9dd10Ccea3A837aef5c',
                'decimals': 18,
            },
            {
                'name': 'SNX',
                'address': '0x50B728D8D964fd00C2d0AAD81718b71311feF68a',
                'decimals': 18,
            },
            {
                'name': '1INCH',
                'address': '0x9c2C5fd7b07E95EE044DDeba0E97a665F142394f',
                'decimals': 18,
            },
            {
                'name': 'YFI',
                'address': '0xDA537104D6A5edd53c6fBba9A898708E465260b6',
                'decimals': 18,
            },
        ],
        'sides' : [
            {
                'name': 'WMATIC',
                'address': '0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270',
                'decimals': 18,
                'minAmount': 2,
            },
            {
                'name': 'WETH',
                'address': '0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619',
                'decimals': 18,
                'minAmount': 0.001,
            },
            {
                'name': 'USDC',
                'address': '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174',
                'decimals': 6,
                'minAmount': 5,
            },
        ],
    },
}

import json
def readJson(filename: str) -> dict:
    f = open(filename, 'r')
    parsedJson = json.load(f)
    f.close()
    return parsedJson

abi = {
    'IUniswapRouter': readJson('abi/IUniswapRouter.json'),
    'IUniswapFactory': readJson('abi/IUniswapFactory.json'),
    'IUniswapPair': readJson('abi/IUniswapPair.json'),
    'IExchangeOracle': readJson('abi/IExchangeOracle.json'),
}