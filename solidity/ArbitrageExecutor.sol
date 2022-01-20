pragma solidity >=0.5;

import "./SafeMath.sol";

interface IUniswapV2Router {
    function swapExactTokensForTokens(uint amountIn, uint amountOutMin, address[] calldata path, address to, uint deadline) external returns (uint[] memory amounts);
    function getAmountsOut(uint amountIn, address[] calldata path) external view returns (uint[] memory amounts);
}

interface IUniswapV2Pair {
    function swap(uint amount0Out, uint amount1Out, address to, bytes calldata data) external;

    function getReserves() external view returns (uint112 reserve0, uint112 reserve1, uint32 blockTimestampLast);
    function factory() external view returns (address);
    function token0() external view returns (address);
    function token1() external view returns (address);
}

interface IUniswapV2Callee {
    function uniswapV2Call(address sender, uint amount0, uint amount1, bytes calldata data) external;
}

interface IApeCallee {
    function apeCall(address sender, uint amount0, uint amount1, bytes calldata data) external;
}

interface IERC20 {
    function balanceOf(address owner) external view returns (uint256 balance);
    function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
    function transfer(address to, uint256 amount) external returns (bool);
    function approve(address spender, uint256 amount) external returns (bool);
}


contract ArbitrageExecutor is IUniswapV2Callee, IApeCallee {
    using SafeMath for uint;
    address private owner;

    constructor() {
        owner = msg.sender;
    }


    // given an input amount of an asset and pair reserves, returns the maximum output amount of the other asset
    function getAmountOut(uint amountIn, uint reserveIn, uint reserveOut, uint r) internal pure returns (uint amountOut) {
        // require(amountIn > 0, 'UniswapV2Library: INSUFFICIENT_INPUT_AMOUNT');
        // require(reserveIn > 0 && reserveOut > 0, 'UniswapV2Library: INSUFFICIENT_LIQUIDITY');
        uint amountInWithFee = amountIn.mul(r);
        uint numerator = amountInWithFee.mul(reserveOut);
        uint denominator = reserveIn.mul(10000).add(amountInWithFee);
        amountOut = numerator / denominator;
    }

    function _getAmountOut(uint amountIn, address tokenInAddr, address pairAddr, uint r) internal view returns (uint256 amountOut) {
        IUniswapV2Pair pair = IUniswapV2Pair(pairAddr);
        (uint112 reserve0, uint112 reserve1, )= pair.getReserves();
        amountOut = pair.token0() == tokenInAddr ? getAmountOut(amountIn, reserve0, reserve1, r) : getAmountOut(amountIn, reserve1, reserve0, r);
    }
    
   
    // given an output amount of an asset and pair reserves, returns a required input amount of the other asset
    function getAmountIn(uint amountOut, uint reserveIn, uint reserveOut, uint r) internal pure returns (uint amountIn) {
        // require(amountOut > 0, 'UniswapV2Library: INSUFFICIENT_OUTPUT_AMOUNT');
        // require(reserveIn > 0 && reserveOut > 0, 'UniswapV2Library: INSUFFICIENT_LIQUIDITY');
        uint numerator = reserveIn.mul(amountOut).mul(10000);
        uint denominator = reserveOut.sub(amountOut).mul(r);
        amountIn = (numerator / denominator).add(1);
    }

    function _getAmountIn(uint amountOut, address tokenOutAddr, address pairAddr, uint r) internal view returns (uint256 amountIn) {
        IUniswapV2Pair pair = IUniswapV2Pair(pairAddr);
        (uint112 reserve0, uint112 reserve1, )= pair.getReserves();
        amountIn = pair.token0() == tokenOutAddr ? getAmountIn(amountOut, reserve1, reserve0, r) : getAmountIn(amountOut, reserve0, reserve1, r);
    }

 //////////////////////////////////
 //////////////////////////////////
 //////////////////////////////////
 //////////////////////////////////
 //////////////////////////////////
 //////////////////////////////////

    function _callExecute(address sender, uint amount0, uint amount1, bytes calldata data) private {
        (uint initialAmount, uint finalAmount, address pairSellAddr, address sideTokenAddr, address baseTokenAddr) = abi.decode(data, (uint, uint, address, address, address));

        // Swap BaseToken with SideToken
        IERC20(baseTokenAddr).transfer(pairSellAddr, amount0 + amount1);
        IUniswapV2Pair(pairSellAddr).swap(
            baseTokenAddr < sideTokenAddr ? 0 : finalAmount,
            baseTokenAddr < sideTokenAddr ? finalAmount : 0,
            sender,
            new bytes(0)
        );
        // Pay back in SideToken 
        IERC20(sideTokenAddr).transfer(msg.sender, initialAmount);
    }

    function execute(uint initialAmount, uint profit,
                     address pairBuyAddr, uint pairBuyR,
                     address pairSellAddr, uint pairSellR,
                     address sideTokenAddr, address baseTokenAddr) public {
        // Initial Check
        uint middleAmount = _getAmountOut(initialAmount, sideTokenAddr, pairBuyAddr, pairBuyR);
        uint finalAmount = _getAmountOut(middleAmount, baseTokenAddr, pairSellAddr, pairSellR);
        require(finalAmount >= initialAmount + profit, "ArbitrageExecutor: Initial check failed!");

        // Borow BaseToken
        IUniswapV2Pair(pairBuyAddr).swap(
            baseTokenAddr < sideTokenAddr ? middleAmount : 0,
            baseTokenAddr < sideTokenAddr ? 0 : middleAmount,
            address(this),
            abi.encode(initialAmount, finalAmount, pairSellAddr, sideTokenAddr, baseTokenAddr)
        );
        IERC20(sideTokenAddr).transfer(owner, finalAmount - initialAmount);
    }

    function withdrawToken(address tokenAddr) external {
        require(owner == msg.sender, "Owner");
        IERC20(tokenAddr).transfer(owner, IERC20(tokenAddr).balanceOf(address(this)));
    }

    function uniswapV2Call(address sender, uint amount0, uint amount1, bytes calldata data) override external {
        _callExecute(sender, amount0, amount1, data);
    }
    function apeCall(address sender, uint amount0, uint amount1, bytes calldata data) override external {
        _callExecute(sender, amount0, amount1, data);
    }
}