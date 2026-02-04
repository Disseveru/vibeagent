# VibeAgent User Guide

## For Complete Beginners (No Coding Required)

### What is VibeAgent?

VibeAgent is a tool that helps you make money in DeFi (Decentralized Finance) without knowing how to code. It finds profitable opportunities and creates the transactions for you, which you can execute through your Avocado multi-sig wallet.

### What You Need

1. **Avocado Wallet**: A multi-sig wallet from Instadapp ([avocado.instadapp.io](https://avocado.instadapp.io))
2. **Some ETH**: For gas fees (transaction costs)
3. **This Software**: VibeAgent (you're here!)

### Step-by-Step Guide

#### Step 1: Install VibeAgent

1. Download this repository
2. Open a terminal/command prompt
3. Navigate to the vibeagent folder
4. Run: `pip install -r requirements.txt`

#### Step 2: Configure Your Settings

1. Copy `.env.example` to `.env`
2. Edit `.env` file:
   - Add your Alchemy/Infura RPC URL (free tier works)
   - Add your Avocado wallet address
   - Optionally add OpenAI API key for enhanced AI

#### Step 3: Start the Web Interface

Run this command:
```bash
python -m vibeagent.cli web
```

Open your browser and go to: `http://localhost:5000`

#### Step 4: Find Opportunities

**For Arbitrage:**
1. Click the "Arbitrage" tab
2. Enter two token addresses (e.g., WETH and USDC)
3. Select which DEXes to compare
4. Click "Scan for Arbitrage"

**For Liquidations:**
1. Click the "Liquidation" tab
2. Select a protocol (Aave or Compound)
3. Click "Scan for Liquidations"

#### Step 5: Export to Avocado

1. Review the opportunity found
2. Click "Export for Avocado Transaction Builder"
3. Copy the JSON that appears

#### Step 6: Execute in Avocado

1. Go to [avocado.instadapp.io](https://avocado.instadapp.io)
2. Connect your wallet
3. Open "Transaction Builder"
4. Click "Import Batch"
5. Paste the JSON you copied
6. Review all transactions carefully
7. Click "Simulate" to test (recommended!)
8. If simulation succeeds, gather signatures from your multi-sig owners
9. Execute the transaction

### Understanding the Strategies

#### Arbitrage
- Buys a token where it's cheap
- Sells it where it's expensive
- Uses a flashloan (borrowed money you repay instantly)
- Profit = Price difference - Fees

#### Liquidation
- Finds loans that are undercollateralized
- Repays part of the loan for someone
- Gets their collateral at a discount
- Sells the collateral for profit
- Profit = Liquidation bonus - Fees

### Safety Tips

1. **Start Small**: Test with tiny amounts first
2. **Simulate First**: Always simulate before executing
3. **Check Gas**: High gas prices eat into profits
4. **Review Everything**: Read all transaction details
5. **Multi-Sig**: Use multiple signers for large amounts
6. **Market Volatility**: Prices can change quickly
7. **Slippage**: Allow some price movement tolerance

### Common Token Addresses

**Ethereum Mainnet:**
- WETH: `0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2`
- USDC: `0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48`
- USDT: `0xdAC17F958D2ee523a2206206994597C13D831ec7`
- DAI: `0x6B175474E89094C44Da98b954EedeAC495271d0F`

### Troubleshooting

**"Agent not initialized"**
- Make sure you filled in your wallet address and clicked "Initialize Agent"

**"No opportunities found"**
- This is normal - profitable opportunities are rare
- Try different token pairs
- Check during high volatility periods

**"Simulation failed"**
- Gas price might be too high
- Slippage might be too low
- Opportunity might have disappeared

**"Transaction failed"**
- Price changed (frontrun)
- Not enough gas
- Token allowances not set

### Getting Help

- Read the full README.md
- Check examples/ folder for code samples
- Join our Discord community
- Open an issue on GitHub

### Advanced Users

Once comfortable with the web interface, try the CLI for faster operations:

```bash
# Initialize
python -m vibeagent.cli init-agent --network ethereum --wallet 0xYour...

# Quick arbitrage scan
python -m vibeagent.cli arbitrage --token-a 0x... --token-b 0x...

# Quick liquidation scan  
python -m vibeagent.cli liquidation --protocol aave
```

---

Remember: **Always understand what you're doing before executing transactions!**
