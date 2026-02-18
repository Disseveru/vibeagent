# 🚀 VibeAgent

**AI-Powered DeFi Strategy Generator for Instadapp Avocado Multi-Sig Wallet**

VibeAgent is an intelligent coding assistant that helps you create and execute sophisticated DeFi strategies including flashloan arbitrage and liquidations - all without writing a single line of code!

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Disseveru/vibeagent)

## ✨ Features

- 🤖 **AI-Powered Strategy Generation**: Automatically detects and creates optimal DeFi strategies
- 🔄 **Autonomous Arbitrage Agent**: Continuously scans and executes profitable opportunities automatically
- 💎 **Flashloan Arbitrage**: Find price differences across DEXes and profit with zero capital
- 🎯 **Smart Liquidations**: Identify and execute profitable liquidations on lending protocols
- 💳 **Reown AppKit Wallet Integration**: Connect with 300+ wallets including MetaMask, Trust Wallet, Coinbase Wallet, Rainbow, and more
- 🔐 **Avocado Multi-Sig Integration**: Seamlessly integrates with Instadapp's Avocado wallet transaction builder
- 🛡️ **Safety Checks**: Configurable profit thresholds, gas limits, and blacklists
- 📊 **Real-Time Dashboard**: Live monitoring of scans, executions, and profits
- 🌐 **No-Code Web Interface**: Beautiful, intuitive UI for non-technical users
- ⚡ **CLI Support**: Command-line interface for quick operations
- 🔗 **Multi-Chain**: Supports Ethereum, Polygon, and Arbitrum
- 📱 **Android PWA Support**: Install as a native-like app on Android devices

## 💳 Wallet Integration (NEW!)

VibeAgent now supports seamless wallet connection through Reown AppKit:

- **300+ Wallets Supported**: MetaMask, Trust Wallet, Coinbase Wallet, Rainbow, Ledger, and more
- **One-Click Connection**: Simply click "Connect Wallet" and choose your preferred wallet
- **Real-Time Balance**: See your wallet balance update in real-time
- **Network Switching**: Easily switch between Ethereum, Polygon, and Arbitrum
- **Transaction History**: View all your transactions with blockchain explorer links
- **Safety First**: Manual approval mode, minimum profit thresholds, and gas price limits
- **Your Wallet, Your Control**: You maintain full custody of your funds

See the [Wallet Integration Guide](docs/WALLET_INTEGRATION.md) for detailed setup and usage.

## 🤖 Autonomous Agent

NEW! VibeAgent now includes a fully autonomous agent that:

- **Continuously Monitors** arbitrage opportunities across Ethereum, Polygon, and Arbitrum
- **Executes Automatically** when profitable opportunities are detected (configurable)
- **Safety First** with minimum profit thresholds, gas limits, and blacklists
- **Manual Approval Mode** for reviewing transactions before execution
- **Real-Time Updates** showing scan status, execution stats, and profits
- **Complete Logging** of all operations for audit trail
- **Profit Tracking** with automatic transfer to your Avocado wallet

See the [Autonomous Agent Documentation](docs/AUTONOMOUS_AGENT.md) for detailed setup and usage.

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
3. Choose Arbitrage or Liquidation tab
4. Enter token addresses or protocol details
5. Click "Scan" to find opportunities
6. Click "Export for Avocado Transaction Builder"
7. Copy the JSON and import it into [avocado.instadapp.io](https://avocado.instadapp.io)

#### 📱 Android Installation (PWA)

Install VibeAgent as a Progressive Web App on your Android device:

1. Open the web interface in Chrome on your Android device
2. Tap the "Install" button when prompted, or
3. Tap the menu (⋮) → "Add to Home screen" or "Install app"
4. The app icon will appear on your home screen
5. Launch it like any native Android app!

See [Android Installation Guide](docs/ANDROID_INSTALL.md) for detailed instructions.

#### 📱 Native Android (Reown Core)

Building a native client instead of the PWA? Install Reown Android Core with the same `REOWN_PROJECT_ID` and point it at the VibeAgent APIs. See [Reown Android Core Setup](docs/REOWN_ANDROID_CORE.md).

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

## 🎨 Web Interface Preview

The web interface provides:
- 🎯 Simple configuration with network selection
- 🔍 Opportunity scanner with real-time analysis
- 📊 Strategy visualization
- ⚡ One-click export to Avocado
- ⚠️ Risk warnings and gas estimates
- 📱 Mobile-responsive design
- 🤖 Progressive Web App for Android devices

## 🛡️ Security

- ✅ Strategies are simulated before execution
- ✅ Gas estimates provided upfront
- ✅ Risk warnings for high slippage or complexity
- ✅ Works with multi-sig wallets for added security
- ✅ No private keys stored - integrates with your existing wallet
- ⚠️ Always review transactions before signing
- ⚠️ Test with small amounts first

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
