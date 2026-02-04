# Installation & Setup Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

## Quick Setup (Recommended)

### For Linux/Mac:
```bash
git clone https://github.com/Disseveru/vibeagent.git
cd vibeagent
./setup.sh
```

### For Windows:
```bash
git clone https://github.com/Disseveru/vibeagent.git
cd vibeagent
setup.bat
```

The setup script will:
1. Create a virtual environment
2. Install all dependencies
3. Create a .env configuration file

## Manual Setup

If you prefer manual setup:

1. **Clone the repository**
```bash
git clone https://github.com/Disseveru/vibeagent.git
cd vibeagent
```

2. **Create virtual environment**
```bash
python -m venv venv
```

3. **Activate virtual environment**
- Linux/Mac: `source venv/bin/activate`
- Windows: `venv\Scripts\activate`

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

5. **Configure environment**
```bash
cp .env.example .env
```

Edit `.env` with your settings:
- Add your RPC URLs (get free tier from Alchemy or Infura)
- Add your Avocado wallet address
- Optionally add OpenAI API key

## Configuration

### Required Settings

Edit `.env` file:

```env
# RPC URLs (Required)
ETHEREUM_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY
POLYGON_RPC_URL=https://polygon-mainnet.g.alchemy.com/v2/YOUR_KEY
ARBITRUM_RPC_URL=https://arb-mainnet.g.alchemy.com/v2/YOUR_KEY

# Your Avocado Wallet (Required)
AVOCADO_WALLET_ADDRESS=0xYourWalletAddressHere
```

### Optional Settings

```env
# OpenAI for enhanced AI features (Optional)
OPENAI_API_KEY=sk-...

# Strategy parameters (Optional)
MIN_PROFIT_USD=50
MAX_GAS_PRICE_GWEI=100
FLASH_LOAN_PROVIDER=aave_v3

# Web interface (Optional)
FLASK_PORT=5000
FLASK_DEBUG=false
```

## Getting RPC URLs

### Option 1: Alchemy (Recommended)
1. Go to [alchemy.com](https://www.alchemy.com/)
2. Sign up for free
3. Create a new app
4. Copy the HTTPS URL

### Option 2: Infura
1. Go to [infura.io](https://infura.io/)
2. Sign up for free
3. Create a new project
4. Copy the project endpoint

## Getting Avocado Wallet

1. Go to [avocado.instadapp.io](https://avocado.instadapp.io)
2. Connect your wallet
3. Create or import Avocado multi-sig wallet
4. Copy your Avocado wallet address

## Verification

Test your installation:

```bash
python test_vibeagent.py
```

You should see:
```
✓ Core modules imported successfully
✓ VibeAgent initialized
✓ Arbitrage analysis works
✓ Strategy generation works
✓ Avocado integration initialized
✓ Transaction batch generation works
✓ Simulation works
✅ All tests passed!
```

## Usage

### Web Interface (No-Code)
```bash
vibeagent web
# or
python -m vibeagent.cli web
```

Then open: http://localhost:5000

### Command Line Interface
```bash
# Initialize
vibeagent init-agent --network ethereum --wallet 0xYour...

# Scan for arbitrage
vibeagent arbitrage --token-a 0x... --token-b 0x...

# Scan for liquidations
vibeagent liquidation --protocol aave

# See all commands
vibeagent --help
```

## Troubleshooting

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### RPC Connection Issues
- Check your RPC URL is correct
- Verify you haven't exceeded free tier limits
- Try a different RPC provider

### Web Interface Won't Start
```bash
# Check if port 5000 is available
lsof -i :5000  # Mac/Linux
netstat -ano | findstr :5000  # Windows

# Use different port
FLASK_PORT=8080 vibeagent web
```

### Permission Denied (Linux/Mac)
```bash
chmod +x setup.sh
```

## Next Steps

1. Read the [User Guide](docs/USER_GUIDE.md)
2. Check [Examples](examples/)
3. Review [README.md](README.md) for features
4. Join our community for support

## Updating

To update to the latest version:

```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

## Uninstall

```bash
# Deactivate virtual environment
deactivate

# Remove directory
cd ..
rm -rf vibeagent
```

---

Need help? Open an issue on GitHub or join our Discord community.
