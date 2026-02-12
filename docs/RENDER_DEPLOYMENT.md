# 🚀 Deploying VibeAgent to Render

This guide will walk you through deploying VibeAgent to Render so you can access it via web browser (Google Chrome) from anywhere.

## Why Render?

Render is a modern cloud platform that makes deployment simple:
- ✅ **Free tier available** - Start without paying
- ✅ **Easy deployment** - Connect your GitHub repo and deploy
- ✅ **Automatic HTTPS** - Secure connection out of the box
- ✅ **Custom domain support** - Use your own domain if you want
- ✅ **Automatic deployments** - Updates when you push to GitHub

## Prerequisites

Before you start, make sure you have:
1. A [GitHub account](https://github.com) with the VibeAgent repository
2. A [Render account](https://render.com) (free to sign up)
3. RPC URLs from [Alchemy](https://www.alchemy.com) or [Infura](https://www.infura.io) (free tier available)
4. (Optional) An OpenAI API key for enhanced AI features

## Step-by-Step Deployment

### 1. Fork or Clone the Repository

If you haven't already, fork the VibeAgent repository to your GitHub account:
- Go to https://github.com/Disseveru/vibeagent
- Click the "Fork" button in the top right

### 2. Sign Up for Render

1. Go to https://render.com
2. Click "Get Started for Free"
3. Sign up with your GitHub account (recommended) or email
4. Verify your email address

### 3. Create a New Web Service

1. From your Render dashboard, click **"New +"** in the top right
2. Select **"Web Service"**
3. Connect your GitHub account if you haven't already
4. Find and select your **vibeagent** repository
5. Click **"Connect"**

### 4. Configure Your Web Service

Render will auto-detect the configuration from `render.yaml`, but verify these settings:

**Basic Settings:**
- **Name**: `vibeagent` (or choose your own)
- **Region**: Choose closest to you (e.g., Oregon, Frankfurt)
- **Branch**: `main`
- **Root Directory**: Leave empty
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `bash start.sh`

**Instance Type:**
- For testing: **Free** (will spin down after 15 minutes of inactivity)
- For production: **Starter** ($7/month) or higher (stays always on)

### 5. Set Environment Variables

Click **"Advanced"** and add these environment variables:

**Required Variables:**

| Variable | Value | Description |
|----------|-------|-------------|
| `PORT` | 10000 | Port for the web server (auto-set by Render) |
| `ETHEREUM_RPC_URL` | `https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY` | Your Alchemy/Infura Ethereum RPC URL |
| `POLYGON_RPC_URL` | `https://polygon-mainnet.g.alchemy.com/v2/YOUR_KEY` | Your Alchemy/Infura Polygon RPC URL |
| `ARBITRUM_RPC_URL` | `https://arb-mainnet.g.alchemy.com/v2/YOUR_KEY` | Your Alchemy/Infura Arbitrum RPC URL |

**Optional Variables:**

| Variable | Value | Description |
|----------|-------|-------------|
| `OPENAI_API_KEY` | `sk-...` | OpenAI API key for enhanced AI features |
| `MIN_PROFIT_USD` | `50` | Minimum profit threshold in USD |
| `MAX_GAS_PRICE_GWEI` | `100` | Maximum gas price willing to pay |
| `FLASK_DEBUG` | `false` | Keep as false for production |

**Getting RPC URLs (Free):**
1. Go to [Alchemy](https://www.alchemy.com) or [Infura](https://www.infura.io)
2. Sign up for a free account
3. Create a new app for Ethereum, Polygon, and Arbitrum
4. Copy the HTTPS RPC URLs and paste them into Render

### 6. Deploy Your Service

1. Click **"Create Web Service"** at the bottom
2. Render will start building and deploying your app
3. Wait 2-5 minutes for the initial deployment
4. You'll see logs in real-time showing the deployment progress

### 7. Access Your VibeAgent

Once deployed, you'll see:
- **URL**: `https://your-service-name.onrender.com`
- **Status**: "Live" with a green indicator

Click the URL to open VibeAgent in your browser (Google Chrome)!

## Using VibeAgent on Render

### First Time Setup

1. Open your Render URL in Google Chrome
2. You'll see the VibeAgent web interface
3. Enter your Avocado wallet address
4. Select your network (Ethereum, Polygon, or Arbitrum)
5. Click "Initialize Agent"
6. Start scanning for arbitrage or liquidation opportunities!

### Accessing from Any Device

Your VibeAgent is now accessible from:
- 🖥️ **Desktop**: Any computer with a browser
- 📱 **Mobile**: Your phone or tablet
- 🌍 **Anywhere**: As long as you have internet

Simply bookmark your Render URL for easy access.

## Free Plan vs Paid Plan

### Free Plan
- ✅ Perfect for testing and learning
- ✅ Full functionality
- ⚠️ Spins down after 15 minutes of inactivity
- ⚠️ Takes 30-60 seconds to wake up on first request
- ⚠️ Limited to 750 hours per month

**Best for**: Testing, learning, occasional use

### Starter Plan ($7/month)
- ✅ Always on - no spin down
- ✅ Instant response
- ✅ Better for production use
- ✅ Priority support

**Best for**: Regular use, production strategies

### Professional Plan ($25/month and up)
- ✅ More resources (CPU, RAM)
- ✅ Multiple instances
- ✅ Better performance
- ✅ High availability

**Best for**: Heavy usage, multiple users

## Recommendation

**Start with the free plan!** Here's why:
1. Test everything works correctly
2. Make sure you understand how to use VibeAgent
3. Execute a few strategies to validate the setup
4. If you use it regularly and the spin-down bothers you, upgrade to Starter

## Monitoring Your Deployment

### View Logs
1. Go to your Render dashboard
2. Click on your vibeagent service
3. Click "Logs" tab
4. See real-time logs of all activity

### Check Status
- Green "Live" = Service is running
- Yellow "Building" = Service is deploying
- Red "Failed" = Check logs for errors

## Updating Your Deployment

When you make changes to your GitHub repository:
1. Push changes to the `main` branch
2. Render automatically detects the changes
3. It rebuilds and redeploys automatically
4. Takes 2-5 minutes for updates to go live

To disable auto-deploy:
- Go to Settings > Build & Deploy
- Turn off "Auto-Deploy"

## Custom Domain (Optional)

Want to use your own domain like `vibeagent.yourdomain.com`?

1. Go to your service settings
2. Click "Custom Domains"
3. Add your domain
4. Follow DNS setup instructions
5. Render provides free SSL certificate

## Troubleshooting

### Service Won't Start
**Check**: Environment variables are set correctly
**Solution**: Verify all RPC URLs are valid

### "Agent Not Initialized" Error
**Check**: RPC URLs are working
**Solution**: Test your Alchemy/Infura URLs in a browser

### Slow Response Time
**Check**: Using free plan with spin-down
**Solution**: Upgrade to Starter plan or wait 30-60 seconds on first request

### Build Failed
**Check**: Logs for specific error
**Solution**: Most common issues:
- Missing environment variables
- Invalid Python syntax
- Missing dependencies

### Can't Connect to Blockchain
**Check**: RPC URL environment variables
**Solution**: Verify Alchemy/Infura keys are correct and not rate-limited

## Security Best Practices

1. **Never commit API keys** to GitHub
2. **Use environment variables** for all secrets
3. **Rotate API keys** regularly
4. **Use HTTPS only** (Render provides this automatically)
5. **Review transactions** before executing in Avocado
6. **Start with small amounts** to test

## Cost Estimate

### Free Plan
- **Cost**: $0/month
- **Limitations**: Spins down after inactivity
- **Good for**: Testing, learning, occasional use

### Starter Plan
- **Cost**: $7/month
- **Benefits**: Always on, no spin down
- **Good for**: Regular use, production

### With Additional Services
- Alchemy/Infura RPC: Free tier sufficient for most use
- OpenAI API: ~$5-20/month depending on usage
- **Total for production**: $7-27/month

## Next Steps

After deploying to Render:

1. ✅ **Bookmark your URL** for easy access
2. ✅ **Install as PWA** on Android (see [Android Install Guide](ANDROID_INSTALL.md))
3. ✅ **Test with small amounts** first
4. ✅ **Join the community** on Discord for support
5. ✅ **Read the User Guide** for detailed usage instructions

## Support

Need help?
- 📖 Read the [User Guide](USER_GUIDE.md)
- 💬 Join our [Discord Community](https://discord.gg/vibeagent)
- 🐛 [Report Issues](https://github.com/Disseveru/vibeagent/issues)
- 📧 Email: support@vibeagent.io

## Conclusion

Congratulations! 🎉 You now have VibeAgent running in the cloud, accessible from any browser, ready to help you find and execute DeFi strategies.

**Remember**: Start with the free plan, test everything thoroughly, and upgrade to a paid plan only if you need always-on availability.

Happy DeFi trading! 🚀💎

---

**Built with ❤️ for the DeFi community**
