# WalletConnect Setup Guide

This guide explains how to set up Reown AppKit with WalletConnect for mobile wallet support in VibeAgent.

## Overview

VibeAgent supports wallet connections through:
1. **Injected providers** (MetaMask browser extension, MetaMask in-app browser, etc.)
2. **WalletConnect** (for mobile wallets like MetaMask Mobile, Trust Wallet, Rainbow, etc.)

## Getting a Reown Project ID

WalletConnect requires a project ID from Reown (formerly WalletConnect Cloud):

1. Go to [https://cloud.reown.com/](https://cloud.reown.com/)
2. Sign up or log in
3. Create a new project
4. Copy your Project ID

## Configuration

### Environment Variable

Add your Reown Project ID to your `.env` file:

```bash
REOWN_PROJECT_ID=your_project_id_here
```

### For Production Deployment

Make sure to set the `REOWN_PROJECT_ID` environment variable in your hosting platform:

- **Render.com**: Add it in Dashboard → Environment → Environment Variables
- **Heroku**: `heroku config:set REOWN_PROJECT_ID=your_id`
- **Vercel**: Add it in Project Settings → Environment Variables
- **Docker**: Pass it with `-e REOWN_PROJECT_ID=your_id`

## How It Works

### Desktop Browsers

When users access VibeAgent from a desktop browser:
- If MetaMask extension is installed → uses injected provider (window.ethereum)
- If no extension → shows error message suggesting to install MetaMask

### Mobile Browsers

When users access VibeAgent from a mobile browser:
- If opened in MetaMask in-app browser → uses injected provider
- If opened in regular mobile browser → uses WalletConnect modal/deep linking

### WalletConnect Flow

1. User clicks "Connect with Reown"
2. App detects no injected provider
3. WalletConnect Universal Provider initializes
4. QR code modal appears (desktop) or deep link opens wallet app (mobile)
5. User scans QR code or approves in wallet app
6. Connection established via WalletConnect bridge

## Supported Wallets

Via injected provider:
- MetaMask (extension & in-app browser)
- Coinbase Wallet
- Brave Wallet
- Trust Wallet (in-app browser)

Via WalletConnect:
- MetaMask Mobile
- Trust Wallet
- Rainbow
- Argent
- Zerion
- ImToken
- 300+ other WalletConnect-compatible wallets

## Troubleshooting

### "WalletConnect libraries are not available"

This error occurs when the WalletConnect CDN scripts fail to load. Possible causes:
- Content Security Policy (CSP) blocking external scripts
- Ad blockers
- Network restrictions
- Offline mode

**Solutions:**
1. Disable ad blockers for the site
2. Check browser console for CSP errors
3. Ensure `https://unpkg.com` is accessible
4. For production, consider self-hosting the WalletConnect libraries

### "Connection timeout after 30 seconds"

The user didn't complete the connection flow within 30 seconds.

**Solutions:**
1. Try connecting again
2. Ensure wallet app is installed on mobile
3. Check wallet app is not frozen/crashed

### CDN Scripts Blocked

If you need to self-host the WalletConnect libraries instead of using CDN:

1. Install packages:
   ```bash
   npm install @walletconnect/universal-provider@2.11.0
   npm install @reown/appkit@1.0.2
   ```

2. Build and bundle the scripts:
   ```bash
   npm run build
   ```

3. Update the script tags in `templates/index.html` to point to your bundled files

## Security Considerations

### Project ID Security

The Reown Project ID is **not a secret** and can be safely exposed in client-side code. It's used for:
- Usage analytics
- Rate limiting
- Project identification

However, you should:
- Restrict allowed origins in Reown Cloud dashboard
- Monitor usage to detect abuse
- Rotate the ID if compromised

### Connection Security

- All connections are established peer-to-peer
- Private keys never leave the wallet
- Transactions require user approval in wallet
- WalletConnect uses end-to-end encryption

## Testing

### Desktop Testing

1. With MetaMask installed:
   ```bash
   # Should detect injected provider
   python -m vibeagent.cli web
   # Open http://localhost:5000 and click "Connect with Reown"
   ```

2. Without MetaMask:
   - Open in a browser without MetaMask extension
   - Should show error message suggesting installation

### Mobile Testing

1. MetaMask in-app browser:
   - Open MetaMask app
   - Navigate to browser
   - Visit your VibeAgent URL
   - Should use injected provider

2. Regular mobile browser:
   - Open Safari/Chrome on mobile
   - Visit your VibeAgent URL
   - Click "Connect with Reown"
   - Should trigger WalletConnect modal or deep link

### Manual Test Checklist

- [ ] Desktop Chrome with MetaMask → uses injected provider
- [ ] Desktop Chrome without MetaMask → shows install message
- [ ] Mobile Safari → triggers WalletConnect
- [ ] MetaMask in-app browser → uses injected provider
- [ ] Connection state persists on network switch
- [ ] Disconnection clears state properly
- [ ] Error messages are clear and actionable

## API Reference

### JavaScript Functions

#### `connectWallet()`
Attempts to connect wallet, trying injected provider first, then WalletConnect.

**Returns:** `Promise<boolean>` - true if connected

#### `disconnectWallet()`
Disconnects the current wallet session.

#### `getWalletState()`
Returns current wallet connection state.

**Returns:** 
```javascript
{
  connected: boolean,
  address: string | null,
  chainId: number | null,
  balance: number | null,
  isWalletConnect: boolean
}
```

### Backend Endpoints

#### `POST /api/wallet/connect`
Notifies backend of wallet connection.

**Request:**
```json
{
  "address": "0x...",
  "chainId": 1
}
```

#### `GET /api/wallet/balance/<address>`
Gets wallet balance from blockchain.

#### `GET /api/wallet/state`
Returns all connected wallets (thread-safe).

## Further Reading

- [Reown AppKit Documentation](https://docs.reown.com/appkit/overview)
- [WalletConnect Documentation](https://docs.walletconnect.com/)
- [EIP-1193 Provider API](https://eips.ethereum.org/EIPS/eip-1193)
