# Secure Deployment Guide

## Important Security Notice

**NEVER commit your `.env` file or any credentials to the repository!**

The `.env` file is already in `.gitignore` to prevent accidental commits.

## Setup Instructions

### 1. Local Development

Create a `.env` file in the root directory with your credentials:

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your actual credentials
# DO NOT commit this file!
```

### 2. Production Deployment (Render, Heroku, etc.)

**Do not use `.env` files in production.** Instead, configure environment variables through your hosting platform:

#### Render.com:
1. Go to your service dashboard
2. Navigate to "Environment" section
3. Add each variable individually:
   - `ETHEREUM_RPC_URL`
   - `POLYGON_RPC_URL`
   - `ARBITRUM_RPC_URL`
   - `OPENAI_API_KEY`
   - `AVOCADO_WALLET_ADDRESS`
   - etc.

#### Heroku:
```bash
heroku config:set ETHEREUM_RPC_URL="your-url"
heroku config:set POLYGON_RPC_URL="your-url"
# etc.
```

#### AWS/GCP:
Use AWS Secrets Manager or GCP Secret Manager for production credentials.

## Required Environment Variables

### Blockchain RPC URLs (Required)
```
ETHEREUM_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY
POLYGON_RPC_URL=https://polygon-mainnet.g.alchemy.com/v2/YOUR_KEY
ARBITRUM_RPC_URL=https://arb-mainnet.g.alchemy.com/v2/YOUR_KEY
```

### OpenAI API Key (Optional - for AI strategy generation)
```
OPENAI_API_KEY=sk-proj-YOUR_KEY
```

### Avocado Wallet (Optional - for transaction execution)
```
AVOCADO_WALLET_ADDRESS=0xYourWalletAddress
AVOCADO_API_ENDPOINT=https://api.instadapp.io/avocado
```

## Checking Git Status

Before committing, always verify `.env` is not tracked:

```bash
git status
# Should NOT show .env file
```

If you accidentally added `.env`:

```bash
git rm --cached .env
git commit -m "Remove .env from tracking"
```

## Security Best Practices

1. ✅ Use environment variables for all secrets
2. ✅ Never commit API keys or private keys
3. ✅ Use different credentials for dev/staging/production
4. ✅ Rotate API keys regularly
5. ✅ Use read-only RPC endpoints when possible
6. ✅ Limit wallet permissions to minimum required
7. ✅ Enable 2FA on all accounts (Alchemy, OpenAI, etc.)

## Verifying Setup

Test your configuration:

```bash
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('Ethereum RPC:', 'Configured' if os.getenv('ETHEREUM_RPC_URL') else 'Missing')
print('Polygon RPC:', 'Configured' if os.getenv('POLYGON_RPC_URL') else 'Missing')
print('Arbitrum RPC:', 'Configured' if os.getenv('ARBITRUM_RPC_URL') else 'Missing')
print('Avocado Wallet:', 'Configured' if os.getenv('AVOCADO_WALLET_ADDRESS') else 'Missing')
"
```

## Getting API Keys

- **Alchemy RPC**: https://www.alchemy.com/ (free tier available)
- **OpenAI**: https://platform.openai.com/ (optional, required for AI features)
- **Avocado Wallet**: https://avocado.instadapp.io/ (optional, for execution)
