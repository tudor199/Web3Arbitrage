# Web3Arbitrage

This is a simple and extensible arbitrage bot which works between UniSwapV2 forks. The main ide a is taking advantages on price differences between two Decentralized Exchanges and complete the transaction by using UniSwap's `flashswap` (or optimistically transfer).

By using `flashswap` feature we can trade just by holding some blockchain's native coin in order to pay for the gas fees, this trick allows us to swap even millions of dollars in one transaction without having them in our wallet.

# Setup

The following assumes the use of `python@>=3.6.9`.

Install python requirements using `pip3 install -r requirements.txt`.

Update `secret.py` with your account address and private key.

Default configuration file will run the bot on polygon network, so make sure to have some MATIC in your wallet if you want to generate some profits.

# Run

Run `python3 main.py -p` to preprocess the configuration file, in order to fetch all trading pair's addresses from the blockchain. This step will take around 3 minutes, depending on the amounts of tokens and DEXs, but it is only required just when we modify `configuration.py`.

Start the bot with `python3 main.py`

Stop the bot by a Keyboard Interrupt `CTRL+C`

# Workflow

The Python program work flow is the following:

    * Worker queries the Exchange Oracle to get Reserves of each pair.
    * Worker gives to each group the pairs that corresponds  to its trading tokens.
    * The groups try to find the best input amount between 2 DEXs.
    * If the trade can generate a potential profit, a transaction is submitted on the blockchain to Arbitrage Executor. 

The Solidity Arbitrage Executor work flow is the following:

    * Check if the opportunity is still available in order to save gas.
    * Compute the path's amounts: initial(SideToken) -> middle(BaseToken) -> final(SideToken).
    * Borrow middle(BaseToken) from BuyPair.
    * Swap middle(BaseToken) for final(SideToken) on SellPair.
    * Pay back borrow amount from BuyPair which is worth initial(SideToken)
    * Transfer the difference between final(SideToken) and initial(SideToken) to contract caller.

## Example

Lets suppose we are monitoring the pairs whose tokens are SUSHI(Base Token) and USDC(Side token) and an arbitrage opportunity arises between QuickSwap and SushiSwap, such that we can buy 10,000 SUSHI for 70,000 USDC on QuickSwap and sell them on SushiSwap for 70,100 USDC, taking a profit of 100 USDC.

But we don't need to have 70,000 USDC in our account, we will make use of the `flashswap` feature. First we will borrow 10,000 SUSHI from QuickSwap and sell them on SushiSwap for 70,100 USDC, then we will pay back QuickSwap 70,000 USDC, which is exactly the initial amount that we should have swap for , and keep the rest 100 USDC for us.

# Customizing

In order to customize for a specific network you must first publish `Exchange Oracle Contract` and `Arbitrage Executor Contract` on the blockchain (You can follow the steps here: [Publish a contract using Remix](https://remix-ide.readthedocs.io/en/latest/create_deploy.html)).

Then you need to add a new entry in `models` from `configuration.py`. 


A model entry should respect the template:

```
'custom_network_name' :{
        'provider': Provider HTTP RPC Endpoint (string),
        'exchangOracleAddr': Exchange Oracle Contract's Address (string),
        'executorAddr': Arbitrage Executor Contract's Address (string),
        'routers': [
            {
                'name': Router's Name (string),
                'address': Router's Address (string),
                'r': Percent of the amount after fees (float)
            },
            ...
        ],
        'bases': [
            {
                'name': Base Token's Name (string),
                'address': Base Token's Address (string),
                'decimals': Base Token's decimals (int)
            },
            ...
        ],
        'sides' : [
            {
                'name': Side Token's Name (string),
                'address': Side Token's Address (string),
                'decimals': Side Token's decimals (int),
                'minAmount': Minimum profit to trigger the arbitrage (float),
            },
            ...
        ]
    }
```

**NOTE:**

* **All profits will be received in SideTokens.**

* **r = 1 - swapfee**

After that rerun the steps in **Run** section with custom network as the parameter (`-ncustom_network_name` or `--network custom_network_name`):

Preprocess: `python3 main.py --network custom_network_name -p`

Run: `python3 main.py --network custom_network_name`