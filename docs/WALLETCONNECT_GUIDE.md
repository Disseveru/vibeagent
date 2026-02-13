# 🔗 WalletConnect Integration Guide

## Overview

VibeAgent now supports **WalletConnect (Reown)** integration, allowing you to connect any wallet and execute autonomous arbitrage transactions with AI-powered strategy optimization directly from the web interface.

## Features

✨ **Key Capabilities:**
- 🔐 **Secure Wallet Connection** - Connect any WalletConnect-compatible wallet
- ⚡ **Autonomous Execution** - Execute arbitrage opportunities automatically
- 🛡️ **Safety First** - Comprehensive safety checks before every transaction
- 💰 **Profit Distribution** - Profits sent directly to your connected wallet
- 🌐 **Multi-Chain Support** - Ethereum, Polygon, and Arbitrum
- 📊 **Real-Time Stats** - Track your execution performance
- 🔍 **Gas Optimization** - Automatic gas balance checks and price validation

## Getting Started

### 1. Connect Your Wallet

1. Click the **"🔗 Connect Wallet"** button in the top-right corner
2. Select your desired network (Ethereum, Polygon, or Arbitrum)
3. Enter your wallet address
4. Click "Connect Wallet"

> **Note:** In production, this would use WalletConnect's native browser modal for secure connection. For development/demo, you can enter your wallet address directly.

### 2. Initialize the Agent

1. Select the network for the AI agent (should match your wallet network)
2. Optionally enter an Avocado Multi-Sig wallet address if you want to export strategies
3. Click "Initialize Agent"

### 3. Scan for Opportunities

Navigate to the **Arbitrage** or **Liquidation** tab:

#### Arbitrage Example:
- **Token A:** `0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2` (WETH)
- **Token B:** `0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48` (USDC)
- **DEXes:** `uniswap_v3,sushiswap`

Click **"Scan for Arbitrage"** to analyze opportunities.

### 4. Validate & Execute

Go to the **Execute** tab:

1. Click **"Validate Last Opportunity"** to run safety checks:
   - ✅ Minimum profit threshold met
   - ✅ Wallet connected
   - ✅ Sufficient gas balance
   - ✅ Gas price acceptable
   - ✅ Network validated
   - ✅ Opportunity marked as profitable

2. If validation passes, click **"Execute Opportunity"**

3. Confirm the transaction in your wallet when prompted

## Safety Features

### Automatic Safety Checks

Before every execution, VibeAgent performs comprehensive safety validations:

#### 1. Profit Threshold
- **Default:** $50 minimum profit
- Ensures opportunities are worth the gas costs
- Configurable via `MIN_PROFIT_USD` in `.env`

#### 2. Gas Balance Check
- Verifies sufficient native token (ETH/MATIC) for gas
- Adds 20% buffer for price fluctuations
- Displays current balance and required amount

#### 3. Gas Price Limit
- **Default:** 100 Gwei maximum
- Prevents execution during high gas periods
- Configurable via `MAX_GAS_PRICE_GWEI` in `.env`

#### 4. Network Validation
- Ensures wallet and agent are on the same network
- Prevents cross-chain execution errors

#### 5. Strategy Validation
- Checks opportunity profitability
- Validates strategy structure
- Ensures all required parameters are present

### Configuration

Edit your `.env` file to customize safety parameters:

```env
# Safety Parameters
MIN_PROFIT_USD=50              # Minimum profit threshold in USD
MAX_GAS_PRICE_GWEI=100         # Maximum gas price in Gwei
```

## Execution Modes

### 1. Simulation Mode (Default)

For demonstration and testing, executions run in simulation mode:

- ✅ Generates mock transaction hash
- ✅ Shows estimated profit
- ✅ Validates all safety checks
- ✅ No real blockchain transactions

This allows you to test the system without deploying contracts or spending gas.

### 2. Live Execution (Production)

To enable real execution:

1. Deploy the arbitrage contract (see `contracts/` directory)
2. Update `autonomous_executor.py` with contract address
3. Set `simulated=False` in execution logic
4. Transactions will be signed via WalletConnect

## Execution Statistics

Track your performance with real-time statistics:

- **Successful Executions** - Number of profitable trades executed
- **Failed Executions** - Number of failed attempts
- **Total Profit** - Cumulative profit in USD
- **Status** - Current scanning status

Stats update automatically every 10 seconds while connected.

## Network Support

### Ethereum Mainnet
- **Chain ID:** 1
- **Native Token:** ETH
- **Supported DEXes:** Uniswap V3, SushiSwap
- **Gas Price:** Typically 20-50 Gwei

### Polygon
- **Chain ID:** 137
- **Native Token:** MATIC
- **Supported DEXes:** Uniswap V3, QuickSwap
- **Gas Price:** Typically 30-100 Gwei

### Arbitrum One
- **Chain ID:** 42161
- **Native Token:** ETH
- **Supported DEXes:** Uniswap V3, SushiSwap
- **Gas Price:** Typically 0.1-1 Gwei

## Example Workflow

### Complete Arbitrage Example

1. **Connect Wallet**
   ```
   - Click "Connect Wallet"
   - Select Ethereum
   - Enter: 0xYourWalletAddress
   ```

2. **Initialize Agent**
   ```
   - Select Ethereum
   - Click "Initialize Agent"
   ```

3. **Scan Opportunity**
   ```
   Token A: 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2 (WETH)
   Token B: 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48 (USDC)
   DEXes: uniswap_v3,sushiswap
   ```

4. **Validate**
   ```
   ✓ Profit: $75.00 exceeds minimum
   ✓ Wallet connected
   ✓ Sufficient gas balance (0.5 ETH)
   ✓ Gas price acceptable (45 Gwei)
   ✓ Network validated (ethereum)
   ✓ Opportunity marked as profitable
   ```

5. **Execute**
   ```
   - Click "Execute Opportunity"
   - Confirm transaction
   - Wait for execution
   - Receive profits in wallet
   ```

## Troubleshooting

### "Wallet not connected"
**Solution:** Click "Connect Wallet" button and follow connection steps

### "Insufficient gas balance"
**Solution:** Add more native tokens (ETH/MATIC) to your wallet for gas

### "Gas price too high"
**Solution:** Wait for gas prices to decrease or increase `MAX_GAS_PRICE_GWEI`

### "Network mismatch"
**Solution:** Ensure wallet and agent are on the same network

### "Profit below minimum"
**Solution:** Wait for more profitable opportunities or adjust `MIN_PROFIT_USD`

### "Validation failed"
**Solution:** Check the validation errors and fix issues before executing

## Advanced Features

### Continuous Scanning

For continuous autonomous execution (CLI):

```bash
python -m vibeagent.cli autonomous-scan \
  --network ethereum \
  --wallet 0xYourAddress \
  --token-pairs WETH/USDC,WETH/DAI \
  --dexes uniswap_v3,sushiswap \
  --continuous \
  --interval 60
```

### Custom Profit Thresholds

Set per-execution thresholds:

```python
from vibeagent import AutonomousExecutor

executor = AutonomousExecutor(
    agent=agent,
    wallet_connector=wallet,
    min_profit_usd=100,  # Custom threshold
    max_gas_price_gwei=75
)
```

## API Reference

### Wallet Endpoints

#### Connect Wallet
```
POST /api/wallet/connect
Body: {
  "wallet_address": "0x...",
  "network": "ethereum"
}
```

#### Disconnect Wallet
```
POST /api/wallet/disconnect
```

#### Get Wallet Status
```
GET /api/wallet/status
```

#### Check Gas Balance
```
POST /api/wallet/gas-check
Body: {
  "estimated_gas": 500000
}
```

### Execution Endpoints

#### Validate Opportunity
```
POST /api/execute/validate
Body: {
  "opportunity": {...}
}
```

#### Execute Arbitrage
```
POST /api/execute/arbitrage
Body: {
  "opportunity": {...}
}
```

#### Get Execution Stats
```
GET /api/execute/stats
```

## Security Best Practices

1. **Never Share Private Keys** - VibeAgent never asks for or stores private keys
2. **Verify Transactions** - Always review transaction details before signing
3. **Start Small** - Test with small amounts first
4. **Monitor Gas** - Set appropriate gas price limits
5. **Use Multi-Sig** - Consider using multi-sig wallets for large amounts
6. **Keep Software Updated** - Regularly update VibeAgent and dependencies
7. **Secure Your Environment** - Keep your `.env` file secure
8. **Test on Testnets** - Use testnet deployments before mainnet

## Support & Resources

- 📖 **Documentation:** [GitHub Wiki](https://github.com/Disseveru/vibeagent/wiki)
- 💬 **Discord:** [Community Server](https://discord.gg/vibeagent)
- 🐛 **Issues:** [GitHub Issues](https://github.com/Disseveru/vibeagent/issues)
- 📧 **Email:** info@vibeagent.io

## Disclaimer

⚠️ **Important:** DeFi trading involves significant risks including:
- Smart contract vulnerabilities
- Market volatility
- Gas price fluctuations
- MEV/frontrunning
- Impermanent loss

**Always:**
- Understand the strategies you're executing
- Start with small amounts
- Never invest more than you can afford to lose
- Review all transactions before signing
- Keep your wallet secure

---

**Built with ❤️ for the DeFi community**

*Autonomous arbitrage made simple.*
