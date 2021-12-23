pragma solidity >=0.4.24;

interface IUniswapPair {
    function getReserves() external view returns (uint112 reserve0, uint112 reserve1, uint32 blockTimestampLast);
}

interface IERC20 {
    function balanceOf(address _owner) external view returns (uint256 balance);
}

contract BalanceOracle {
    function getAccountBalance(address[] memory tokensAddrs, uint256 n, address account)
        public view returns (uint256 ethBalance, uint256[] memory tokensBalance) {

        ethBalance = address(account).balance;

        tokensBalance = new uint256[](n);
        for (uint256 i = 0; i < n; i++) {
            tokensBalance[i] = IERC20(tokensAddrs[i]).balanceOf(account);
        }
    }

    function getExchangesState(address[] memory pairsAddrs) public view returns (uint256[] memory reservesToken0, uint256[] memory reservesToken1) {
        uint256 n = pairsAddrs.length;
        reservesToken0 = new uint256[](n);
        reservesToken1 = new uint256[](n);
        for (uint256 i = 0; i < n; i++) {
            (reservesToken0[i], reservesToken1[i], ) = IUniswapPair(pairsAddrs[i]).getReserves();
        }
    }
}