# Reown AppKit Wallet Integration Guide

## Overview

VibeAgent now supports seamless wallet connection through Reown AppKit, enabling you to connect with 300+ wallets including MetaMask, Trust Wallet, Coinbase Wallet, Rainbow, and many more. This integration allows you to use your personal wallet for DeFi operations while maintaining full control of your funds.

## Supported Wallets

The Reown AppKit integration supports:
- **MetaMask** - Browser extension and mobile app
- **Trust Wallet** - Mobile wallet with WalletConnect
- **Coinbase Wallet** - Browser extension and mobile app
- **Rainbow** - Mobile-first Ethereum wallet
- **Ledger** - Hardware wallet support
- **WalletConnect** - Any WalletConnect-compatible wallet
- **And 295+ more wallets!**

## Supported Networks

VibeAgent supports operations on:
- **Ethereum Mainnet** (Chain ID: 1)
- **Polygon** (Chain ID: 137)
- **Arbitrum** (Chain ID: 42161)

## How It Works

### 1. Wallet Connection Flow

```
User clicks "Connect Wallet" 
    ↓
Wallet selector appears (via browser wallet extension)
    ↓
User approves connection
    ↓
Wallet address and balance displayed
    ↓
User can now execute DeFi strategies
```

### 2. Transaction Execution

When a profitable opportunity is found:

1. **Backend Processing**: The VibeAgent AI autonomously identifies arbitrage opportunities and prepares the flash loan transaction
2. **Gas Payment**: Your connected wallet pays the gas fees for the transaction
3. **Flash Loan Execution**: The backend executes the flash loan arbitrage
4. **Profit Distribution**: After repaying the flash loan, profits are automatically sent to your connected wallet
5. **Transaction Tracking**: View transaction hashes with direct links to blockchain explorers

### 3. Safety Features

VibeAgent includes multiple safety features to protect your funds:

- **Manual Approval Toggle**: Require manual confirmation before any transaction (enabled by default)
- **Minimum Profit Threshold**: Only execute trades above $50 profit (configurable)
- **Maximum Gas Price**: Cap gas prices at 100 Gwei (configurable)
- **Real-time Balance Display**: Always see your current wallet balance
- **Transaction History**: View all past transactions with explorer links

## Getting Started

### Step 1: Access VibeAgent Web Interface

Start the web server:
```bash
python -m vibeagent.cli web
```

Navigate to `http://localhost:5000` in your browser.

### Step 2: Connect Your Wallet

1. Click the **"🔗 Connect Wallet"** button at the top of the page
2. Your browser wallet (e.g., MetaMask) will prompt you to connect
3. Approve the connection request
4. Your wallet address and balance will be displayed

### Step 3: Select Network

1. Choose your desired network from the dropdown:
   - Ethereum Mainnet
   - Polygon
   - Arbitrum
2. If prompted, approve the network switch in your wallet
3. The page will update to show your balance on the selected network

### Step 4: Configure Safety Settings

In the **Autonomous Mode** section, set your preferences:

- **✅ Require Manual Approval**: Keep this checked to review each transaction before execution
- **💰 Minimum Profit (USD)**: Set minimum profit threshold (default: $50)
- **⛽ Max Gas Price (Gwei)**: Set maximum gas price you're willing to pay (default: 100)
- **⏱️ Scan Interval**: How often to scan for opportunities (default: 60 seconds)

Click **"Update Configuration"** to save your settings.

### Step 5: Initialize Agent

1. Optionally enter an Avocado Multi-Sig wallet address (or leave empty to use connected wallet)
2. Click **"Initialize Agent"** to start the DeFi strategy engine
3. Wait for confirmation that the agent is initialized

### Step 6: Enable Autonomous Mode (Optional)

1. Check the **"Enable Autonomous Scanning"** checkbox
2. The agent will continuously scan for arbitrage opportunities
3. When a profitable opportunity is found:
   - If manual approval is enabled: You'll see a popup to approve/reject
   - If manual approval is disabled: Transaction executes automatically
4. Monitor results in the **Execution Statistics** and **Transaction History** sections

## Native Android Installation

If you're embedding VibeAgent's Reown AppKit flow into a native Android app, follow the official Reown AppKit Android Core installation guide: [docs.reown.com/appkit/android/core/installation](https://docs.reown.com/appkit/android/core/installation).

## Using Manual Mode

If you prefer not to use autonomous mode, you can manually scan for opportunities:

### Arbitrage Scanner

1. Go to the **Arbitrage** tab
2. Enter Token A and Token B addresses
3. Select which DEXes to compare
4. Click **"Scan for Arbitrage"**
5. Review the opportunity details
6. Export or simulate the strategy

### Liquidation Scanner

1. Go to the **Liquidation** tab
2. Select a lending protocol (Aave, Compound, etc.)
3. Optionally enter a specific account address
4. Click **"Scan for Liquidations"**
5. Review opportunities and execute

## Transaction Monitoring

### View Transaction History

In the **Autonomous Mode** section, scroll to **Transaction History** to see:
- Transaction hash (clickable link to blockchain explorer)
- Transaction status (Success/Pending/Failed)
- Profit amount (if applicable)
- Timestamp

### Check Blockchain Explorer

Click any transaction hash to view full details on:
- **Ethereum**: Etherscan
- **Polygon**: Polygonscan
- **Arbitrum**: Arbiscan

## Security Best Practices

### 1. Wallet Security
- ✅ Use a hardware wallet (Ledger, Trezor) for large amounts
- ✅ Keep your seed phrase secure and never share it
- ✅ Verify transaction details before approving
- ❌ Never approve unlimited token allowances

### 2. Transaction Safety
- ✅ Start with manual approval enabled
- ✅ Set conservative profit thresholds ($50+ recommended)
- ✅ Monitor gas prices and set reasonable limits
- ✅ Test with small amounts first

### 3. Network Safety
- ✅ Verify you're on the correct network before transacting
- ✅ Ensure sufficient balance for gas fees
- ✅ Be aware of network congestion and gas prices

## Troubleshooting

### Wallet Won't Connect

**Problem**: Click "Connect Wallet" but nothing happens

**Solutions**:
1. Install a Web3 wallet browser extension (MetaMask recommended)
2. Refresh the page and try again
3. Check that your wallet extension is unlocked
4. Try a different browser or clear cache

### Network Switch Failed

**Problem**: Error when trying to switch networks

**Solutions**:
1. Manually switch network in your wallet
2. Reload the VibeAgent page
3. Try adding the network manually in your wallet settings

### Transaction Failed

**Problem**: Transaction was submitted but failed

**Solutions**:
1. Check transaction details on blockchain explorer
2. Ensure sufficient balance for gas fees
3. Check if gas price was too low
4. Verify network congestion and try again later

### Balance Not Updating

**Problem**: Wallet balance shows incorrect amount

**Solutions**:
1. Click the refresh button (🔄) next to balance
2. Disconnect and reconnect wallet
3. Check network RPC status

## Advanced Features

### Using with Avocado Multi-Sig

You can use VibeAgent with both:
1. **Personal Wallet**: Direct connection for immediate execution
2. **Avocado Multi-Sig**: Export transactions for multi-sig approval

To use both:
1. Connect your personal wallet for monitoring and testing
2. Enter your Avocado address in the configuration field
3. Export strategies to Avocado transaction builder for secure multi-sig execution

### Custom Network Configuration

For advanced users, you can modify network settings in `/vibeagent/static/reown-wallet.js`:

```javascript
const NETWORKS = {
    ethereum: {
        chainId: 1,
        name: 'Ethereum',
        rpcUrl: 'https://eth.llamarpc.com',
        currency: 'ETH',
        explorerUrl: 'https://etherscan.io'
    },
    // Add custom networks here
};
```

### API Integration

Developers can integrate with the wallet API endpoints:

- `POST /api/wallet/connect` - Handle wallet connection
- `POST /api/wallet/disconnect` - Handle disconnection
- `GET /api/wallet/balance/<address>` - Get wallet balance
- `GET /api/wallet/transaction/<tx_hash>` - Get transaction details
- `GET /api/wallet/state` - Get connection state

## Gas Fee Estimates

Typical gas usage for flash loan arbitrage:

| Network | Est. Gas Units | Gas Price | Est. Cost (USD) |
|---------|---------------|-----------|-----------------|
| Ethereum | 300,000 | 30 Gwei | $10-50 |
| Polygon | 400,000 | 100 Gwei | $0.50-2 |
| Arbitrum | 350,000 | 0.1 Gwei | $0.10-1 |

**Note**: Always ensure your minimum profit threshold is higher than estimated gas costs!

## Support

For issues or questions:
1. Check this documentation first
2. Review the [main README](../README.md)
3. Check the [User Guide](USER_GUIDE.md)
4. Open an issue on GitHub with details about your problem

## Changelog

### Version 1.0.0 (Current)
- ✨ Initial Reown AppKit integration
- ✨ Support for 300+ wallets
- ✨ Ethereum, Polygon, and Arbitrum support
- ✨ Real-time balance display
- ✨ Network switching
- ✨ Transaction history with explorer links
- ✨ Safety features (manual approval, thresholds)
- ✨ Backward compatibility with Avocado integration

## Future Enhancements

Planned features:
- 🔜 Additional network support (Optimism, Base, etc.)
- 🔜 Mobile app with native wallet integration
- 🔜 Advanced analytics dashboard
- 🔜 Profit tracking and reporting
- 🔜 Email/SMS notifications for profitable trades
- 🔜 Multi-wallet management

---

**Remember**: Never invest more than you can afford to lose. DeFi carries risks including smart contract bugs, network congestion, and market volatility. Always use the manual approval feature when testing new strategies.
