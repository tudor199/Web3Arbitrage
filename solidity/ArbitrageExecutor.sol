pragma solidity >=0.4.24;

interface IUniSwapRouter {
    function swapExactTokensForTokens(uint amountIn, uint amountOutMin, address[] calldata path, address to, uint deadline) external returns (uint[] memory amounts);
  function getAmountsOut(uint amountIn, address[] calldata path) external view returns (uint[] memory amounts);
}

interface IERC20 {
    function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
    function transfer(address to, uint256 amount) external returns (bool);
    function approve(address spender, uint256 amount) external returns (bool);
}


contract ArbitrageExecutor {
    address private owner;

    constructor() {
        owner = msg.sender;
    }
    
    function execute(uint initialAmount, address routerBuyAddr, address[] memory pathBuy, address routerSellAddr, address[] memory pathSell) public {
        IUniSwapRouter routerBuy = IUniSwapRouter(routerBuyAddr);
        IUniSwapRouter routerSell = IUniSwapRouter(routerSellAddr);

        // Initial Check
        require(routerSell.getAmountsOut(routerBuy.getAmountsOut(initialAmount, pathBuy)[1], pathSell)[1] > initialAmount, "ArbitrageExecutor: Check failed!");

        IERC20 tokenSide = IERC20(pathBuy[0]);
        IERC20 tokenBase = IERC20(pathBuy[1]);

        tokenSide.transferFrom(msg.sender, address(this), initialAmount);

        // Buy
        tokenSide.approve(routerBuyAddr, initialAmount);
        uint256 middleAmount = routerBuy.swapExactTokensForTokens(initialAmount, 1, pathBuy, address(this), block.timestamp)[1];

        // Sell
        tokenBase.approve(routerSellAddr, middleAmount);
        uint256 finalAmount  = routerSell.swapExactTokensForTokens(middleAmount , 1, pathSell, owner, block.timestamp)[1];

        // Final Check
        require(finalAmount > initialAmount, "ArbitrageExecutor: Execution failed!");

        tokenSide.transfer(owner, finalAmount);
    }
}