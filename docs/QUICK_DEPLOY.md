# ⚡ Quick Deploy to Render

Deploy VibeAgent to Render in 5 minutes and access it from Google Chrome anywhere!

## What You'll Get

✅ Your own VibeAgent instance running 24/7 (or on-demand with free tier)
✅ Accessible from any browser at `https://your-app.onrender.com`
✅ Secure HTTPS connection
✅ Free tier available (or $7/month for always-on)

## Prerequisites

- GitHub account
- Render account (sign up free at https://render.com)
- RPC URLs from Alchemy or Infura (free tier works)

## Deploy in 3 Steps

### Step 1: Prepare Your Repository

1. **Fork this repo** to your GitHub account
2. That's it! The repository is already configured for Render.

### Step 2: Deploy on Render

1. Go to https://render.com and sign in
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub account
4. Select your forked **vibeagent** repository
5. Render will auto-detect the configuration from `render.yaml`
6. Choose your plan:
   - **Free**: Spins down after 15 min (good for testing)
   - **Starter ($7/mo)**: Always on (recommended for production)

### Step 3: Add Environment Variables

In the Render dashboard, add these environment variables:

**Required:**
```
ETHEREUM_RPC_URL = https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY
POLYGON_RPC_URL = https://polygon-mainnet.g.alchemy.com/v2/YOUR_KEY  
ARBITRUM_RPC_URL = https://arb-mainnet.g.alchemy.com/v2/YOUR_KEY
```

**Optional:**
```
OPENAI_API_KEY = sk-your-key-here
```

Click **"Create Web Service"** and wait 2-3 minutes for deployment!

## Get Your RPC URLs (Free)

### Using Alchemy (Recommended)

1. Go to https://www.alchemy.com
2. Sign up for free account
3. Click "Create App"
4. Select chain (Ethereum, Polygon, or Arbitrum)
5. Copy the HTTPS URL
6. Repeat for each chain you want to support

### Using Infura (Alternative)

1. Go to https://www.infura.io
2. Sign up for free account
3. Create new API key
4. Copy the HTTPS URLs for each chain

## What Plan Should I Choose?

### Free Plan - $0/month
**Good for:**
- Testing and learning
- Occasional use
- Experimenting with strategies

**Limitations:**
- Spins down after 15 minutes of inactivity
- Takes 30-60 seconds to wake up
- 750 hours/month limit

**Recommendation:** Start here!

### Starter Plan - $7/month
**Good for:**
- Regular use
- Production strategies
- Always-on availability

**Benefits:**
- No spin down
- Instant response
- Unlimited hours

**Recommendation:** Upgrade after you've tested and like the service

## Access Your VibeAgent

Once deployed, you'll get a URL like:
```
https://vibeagent-xyz123.onrender.com
```

Open it in Google Chrome and start finding DeFi opportunities!

## Troubleshooting

### Deployment Failed?
- Check that all environment variables are set
- Verify RPC URLs are correct
- Check Render logs for specific errors

### Can't Access the Site?
- Free plan takes 30-60 seconds to wake up on first visit
- Check if service is "Live" in Render dashboard
- Try opening in incognito mode

### "Agent Not Initialized" Error?
- RPC URLs might be invalid or rate-limited
- Check environment variables are saved correctly

## Next Steps

1. ✅ Bookmark your Render URL
2. ✅ Test with arbitrage scanner
3. ✅ Try finding liquidation opportunities
4. ✅ Export to Avocado Transaction Builder
5. ✅ Execute your first strategy!

## Need Help?

📖 Full deployment guide: [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)
💬 Discord: https://discord.gg/vibeagent
🐛 Issues: https://github.com/Disseveru/vibeagent/issues

---

**You're ready! Deploy now and start earning DeFi alpha! 🚀💎**
