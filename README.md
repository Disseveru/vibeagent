# 🚀 VibeAgent

**AI-Powered DeFi Strategy Generator for Instadapp Avocado Multi-Sig Wallet**

VibeAgent is an intelligent coding assistant that helps you create and execute sophisticated DeFi strategies including flashloan arbitrage and liquidations - all without writing a single line of code!

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Disseveru/vibeagent)

## ✨ Features

- 🤖 **AI-Powered Strategy Generation**: Automatically detects and creates optimal DeFi strategies
- 💎 **Flashloan Arbitrage**: Find price differences across DEXes and profit with zero capital
- 🎯 **Smart Liquidations**: Identify and execute profitable liquidations on lending protocols
- 🛡️ **MEV Protection**: Built-in MEV (Maximal Extractable Value) detection and protection mechanisms
- 🔐 **Avocado Multi-Sig Integration**: Seamlessly integrates with Instadapp's Avocado wallet transaction builder
- 🌐 **No-Code Web Interface**: Beautiful, intuitive UI for non-technical users
- ⚡ **CLI Support**: Command-line interface for quick operations
- 🔗 **Multi-Chain**: Supports Ethereum, Polygon, and Arbitrum
- 📱 **Android PWA Support**: Install as a native-like app on Android devices

## 🎯 Perfect For

- Non-technical users who want to profit from DeFi opportunities
- Users with Instadapp Avocado multi-sig wallets
- Anyone interested in flashloan arbitrage and liquidations
- DeFi enthusiasts who don't know how to code

## 🚀 Quick Start

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Disseveru/vibeagent.git
cd vibeagent
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your settings
```

### Usage Options

#### Option 1: Web Interface (Recommended for Non-Coders)

Start the web interface:
```bash
python -m vibeagent.cli web
```

Then open your browser at `http://localhost:5000`

**Steps:**
1. Enter your Avocado wallet address and select network
2. Click "Initialize Agent"
3. Choose Arbitrage, Liquidation, or MEV Protection tab
4. Enter token addresses or protocol details
5. Click "Scan" to find opportunities
6. Review MEV risks and protection recommendations (MEV tab)
7. Click "Export for Avocado Transaction Builder"
8. Copy the JSON and import it into [avocado.instadapp.io](https://avocado.instadapp.io)

#### 📱 Android Installation (PWA)

Install VibeAgent as a Progressive Web App on your Android device:

1. Open the web interface in Chrome on your Android device
2. Tap the "Install" button when prompted, or
3. Tap the menu (⋮) → "Add to Home screen" or "Install app"
4. The app icon will appear on your home screen
5. Launch it like any native Android app!

See [Android Installation Guide](docs/ANDROID_INSTALL.md) for detailed instructions.

#### 🌐 Cloud Deployment (Deploy to Render)

Want to access VibeAgent from anywhere via web browser?

**Deploy to Render in 5 minutes:**
1. Fork this repository to your GitHub account
2. Sign up at [Render.com](https://render.com) (free tier available)
3. Create a new Web Service and connect your GitHub repo
4. Render auto-detects configuration from `render.yaml`
5. Add your RPC URLs as environment variables
6. Deploy and access from any browser!

**Benefits:**
- ✅ Access from Google Chrome on any device
- ✅ No need to keep your computer running
- ✅ Free tier available (upgrade to $7/month for always-on)
- ✅ Automatic HTTPS and custom domain support

See [Render Deployment Guide](docs/RENDER_DEPLOYMENT.md) for detailed step-by-step instructions.

#### Option 2: Command Line Interface

Initialize the agent:
```bash
python -m vibeagent.cli init-agent \
  --network ethereum \
  --wallet 0xYourAvocadoWalletAddress
```

Scan for arbitrage opportunities:
```bash
python -m vibeagent.cli arbitrage \
  --token-a 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2 \
  --token-b 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48 \
  --dexes uniswap_v3,sushiswap \
  --output my_arbitrage.json
```

Scan for liquidation opportunities:
```bash
python -m vibeagent.cli liquidation \
  --protocol aave \
  --output my_liquidation.json
```

Simulate before executing:
```bash
python -m vibeagent.cli simulate \
  --strategy-file my_arbitrage.json
```

## 🔧 Configuration

Edit `.env` file:

```env
# RPC URLs (get from Alchemy or Infura)
ETHEREUM_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY
POLYGON_RPC_URL=https://polygon-mainnet.g.alchemy.com/v2/YOUR_API_KEY
ARBITRUM_RPC_URL=https://arb-mainnet.g.alchemy.com/v2/YOUR_API_KEY

# Optional: OpenAI for enhanced AI features
OPENAI_API_KEY=your_openai_key_here

# Avocado Wallet Configuration
AVOCADO_WALLET_ADDRESS=0xYourWalletAddress

# Strategy Parameters
MIN_PROFIT_USD=50
MAX_GAS_PRICE_GWEI=100
```

## 📱 Using with Avocado Multi-Sig Wallet

### What is Avocado?

Avocado is Instadapp's multi-signature smart contract wallet with advanced transaction building capabilities. It allows you to:
- Execute complex multi-step transactions in one go
- Require multiple signers for security
- Build and simulate transactions before execution

### Integration Steps

1. **Generate Strategy**: Use VibeAgent's web or CLI interface to scan for opportunities
2. **Export JSON**: Click "Export for Avocado Transaction Builder" or use CLI export
3. **Import to Avocado**:
   - Go to [avocado.instadapp.io](https://avocado.instadapp.io)
   - Navigate to Transaction Builder
   - Click "Import Batch"
   - Paste the generated JSON
4. **Review**: Check all transaction details
5. **Simulate**: Use Avocado's simulation feature
6. **Execute**: Gather required signatures and execute

## 💡 Strategy Types

### Flashloan Arbitrage

Exploit price differences between DEXes with zero capital:

```
1. Take flashloan from Aave
2. Buy token on DEX A (cheaper)
3. Sell token on DEX B (more expensive)
4. Repay flashloan + fee
5. Keep the profit
```

### Liquidations

Profit from undercollateralized positions in lending protocols:

```
1. Take flashloan for debt token
2. Liquidate undercollateralized position
3. Receive collateral + liquidation bonus
4. Swap collateral back to debt token
5. Repay flashloan
6. Keep the profit
```

## 🛡️ MEV Protection

VibeAgent includes built-in MEV (Maximal Extractable Value) protection to safeguard your transactions from front-running and sandwich attacks.

### What is MEV?

MEV refers to profit that can be extracted by reordering, inserting, or censoring transactions within blocks. MEV bots monitor the public mempool and can exploit opportunities at your expense through:

- **Front-running**: Bots copy your profitable transaction and execute it first with higher gas
- **Sandwich Attacks**: Bots place transactions before and after yours to manipulate prices
- **Back-running**: Bots execute transactions immediately after yours to capture profit

### MEV Protection Features

- 🔍 **MEV Detection**: Automatically scan for MEV opportunities with risk analysis
- ⚠️ **Risk Assessment**: Real-time analysis of front-running and sandwich attack risks
- 🛡️ **Protection Strategies**: Get specific recommendations based on risk level
- 📚 **Educational Content**: Learn about MEV attacks and how to protect yourself
- 🎯 **Risk Scoring**: Each strategy gets a risk score (low/medium/high)

### How to Use MEV Protection

1. Navigate to the **MEV Protection** tab in the web interface
2. **Scan for MEV opportunities** or **analyze existing strategies**
3. Review the risk analysis (front-running and sandwich attack scores)
4. Get protection recommendations based on risk level
5. Apply recommended protections before executing transactions

### Protection Levels

- **Minimal**: Basic slippage and deadline protection (for low-risk transactions)
- **Standard** (Recommended): Slippage protection + tight deadlines + higher gas prices
- **Maximum**: All protections + private mempool (Flashbots) + transaction bundling

### Best Practices

- ✅ Always check MEV risk before executing strategies
- ✅ Use private mempools (Flashbots) for high-value transactions
- ✅ Set minimal slippage tolerance (0.1-0.5%)
- ✅ Use tight transaction deadlines (1-3 minutes)
- ✅ Split large transactions into smaller parts
- ✅ Monitor gas prices and use competitive rates
- ⚠️ Test with small amounts first
- ⚠️ Understand that MEV protection cannot eliminate all risks

### Beginner-Friendly Notice

🚨 **Important for Beginners**: MEV can significantly impact your profits. Our MEV Protection tab provides:
- Easy-to-understand risk scores
- Clear explanations of different attack types
- Step-by-step protection recommendations
- Educational resources to learn more

We recommend starting with the "Learn About MEV" section before executing any strategies.

## 🎨 Web Interface Preview

The web interface provides:
- 🎯 Simple configuration with network selection
- 🔍 Opportunity scanner with real-time analysis
- 🛡️ MEV Protection tab with risk analysis and education
- 📊 Strategy visualization
- ⚡ One-click export to Avocado
- ⚠️ Risk warnings and gas estimates
- 📱 Mobile-responsive design
- 🤖 Progressive Web App for Android devices

## 🛡️ Security

- ✅ Strategies are simulated before execution
- ✅ Gas estimates provided upfront
- ✅ **MEV protection with risk analysis and recommendations**
- ✅ Risk warnings for high slippage or complexity
- ✅ Works with multi-sig wallets for added security
- ✅ No private keys stored - integrates with your existing wallet
- ⚠️ Always review transactions before signing
- ⚠️ Test with small amounts first
- ⚠️ **Check MEV risks before executing any strategy**

## 🔗 Supported Protocols

### DEXes (Arbitrage)
- Uniswap V3
- SushiSwap
- Curve (coming soon)
- Balancer (coming soon)

### Lending Protocols (Liquidation)
- Aave V3
- Compound V3
- More coming soon

### Flashloan Providers
- Aave V3 (default)
- Balancer (coming soon)

## 📚 Examples

### Example 1: WETH/USDC Arbitrage
```bash
python -m vibeagent.cli arbitrage \
  --token-a 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2 \
  --token-b 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48 \
  --dexes uniswap_v3,sushiswap
```

### Example 2: Aave Liquidations
```bash
python -m vibeagent.cli liquidation \
  --protocol aave \
  --output aave_liquidations.json
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - see LICENSE file for details

## ⚠️ Disclaimer

This software is provided "as is" without warranty. DeFi involves risk:
- Smart contract risk
- Market volatility risk
- Liquidation risk
- Gas price fluctuations

**Always:**
- Test with small amounts first
- Understand the strategies you're executing
- Review all transactions before signing
- Never invest more than you can afford to lose

## 🆘 Support

- 📖 [Documentation](https://github.com/Disseveru/vibeagent/wiki)
- 💬 [Discord Community](https://discord.gg/vibeagent)
- 🐛 [Report Issues](https://github.com/Disseveru/vibeagent/issues)

## 🎯 Roadmap

- [ ] Support for more DEXes and protocols
- [ ] Advanced AI strategy optimization
- [ ] Telegram bot interface
- [x] Mobile app (Android PWA available now!)
- [ ] Strategy backtesting
- [ ] Community strategy sharing
- [ ] Automated execution with monitoring

---

**Built with ❤️ for the DeFi community**

*No coding required. Just pure DeFi alpha.*