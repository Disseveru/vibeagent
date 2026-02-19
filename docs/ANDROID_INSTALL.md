# Installing VibeAgent on Android

VibeAgent can be installed as a Progressive Web App (PWA) on your Android device, giving you a native app-like experience without needing to download from the Google Play Store.

## What is a PWA?

A Progressive Web App (PWA) is a web application that can be installed on your device and works like a native app. Benefits include:
- 📱 **Install on Home Screen**: Adds an icon to your home screen just like any other app
- 🚀 **Fast Loading**: Caches resources for quick startup
- 📴 **Offline Support**: Continue using some features even without internet
- 🔒 **Secure**: Uses HTTPS for all communications
- 💾 **No App Store Required**: Install directly from the web

## Installation Steps

### Method 1: Using Chrome Browser (Recommended)

1. **Open Chrome on Android**
   - Navigate to your VibeAgent instance URL (e.g., `http://your-server:5000`)

2. **Install Prompt**
   - You should see a banner at the top saying "Install VibeAgent on your Android device"
   - Tap the **"Install"** button in the banner

3. **Alternative: Menu Method**
   - If you don't see the banner, tap the three dots menu (⋮) in the top right
   - Select **"Add to Home screen"** or **"Install app"**
   - Confirm by tapping **"Install"** or **"Add"**

4. **Find the App**
   - The VibeAgent icon will appear on your home screen
   - You can also find it in your app drawer

5. **Launch the App**
   - Tap the VibeAgent icon to launch
   - The app opens in full-screen mode without the browser UI
   - It works just like a native Android app!

### Method 2: Using Firefox Browser

1. **Open Firefox on Android**
   - Navigate to your VibeAgent instance URL

2. **Install the App**
   - Tap the three dots menu (⋮) in the top right
   - Select **"Install"**
   - Confirm by tapping **"Add"**

3. **Launch the App**
   - Find the VibeAgent icon on your home screen
   - Tap to launch in full-screen mode

### Method 3: Using Samsung Internet Browser

1. **Open Samsung Internet**
   - Navigate to your VibeAgent instance URL

2. **Add to Home Screen**
   - Tap the menu button (three lines)
   - Select **"Add page to"** → **"Home screen"**
   - Tap **"Add"** to confirm

3. **Launch the App**
   - Tap the VibeAgent shortcut on your home screen

## Verifying Installation

After installation, you should see:
- ✅ A "VA" icon on your home screen with the name "VibeAgent"
- ✅ The app opens in full-screen (no browser address bar)
- ✅ A splash screen appears when launching
- ✅ The app works smoothly like a native app

## Features of the Android PWA

### Works Just Like a Native App
- Full-screen experience without browser UI
- Appears in your Recent Apps list
- Notifications support (when implemented)
- Fast loading times

### Offline Capabilities
- Basic UI and cached pages load even without internet
- Smart caching of frequently used resources
- Automatic updates when online

### Security
- All data transmitted over HTTPS
- Uses the same security as the web version
- No additional permissions required

## Updating the App

The PWA automatically updates when:
- You open the app while connected to the internet
- A new version is available on the server

You don't need to manually update from any app store!

## Uninstalling the App

If you need to uninstall VibeAgent:

1. **Long-press the VibeAgent icon** on your home screen
2. Select **"App info"** or drag to **"Uninstall"**
3. Tap **"Uninstall"** to remove the app

Or:

1. Go to **Settings** → **Apps**
2. Find **"VibeAgent"**
3. Tap **"Uninstall"**

## Troubleshooting

### "Install" button doesn't appear
- Make sure you're using Chrome, Firefox, or Samsung Internet
- Ensure you're accessing the site over HTTPS (or HTTP on localhost)
- Try clearing browser cache and reloading the page
- Check if the app is already installed

### App doesn't work offline
- The first time you open the app, it needs internet to cache resources
- Some features (like scanning for opportunities) require an internet connection
- Only cached pages and UI elements work offline

### Can't find the app after installation
- Check your home screen and app drawer
- Look in Settings → Apps to see if it's installed
- Try reinstalling using the browser menu

### App icon looks wrong
- The icon should show "VA" with a purple gradient
- If it shows a generic icon, try uninstalling and reinstalling

## Advantages Over Mobile Browser

Installing as a PWA gives you:

| Feature | Mobile Browser | PWA |
|---------|---------------|-----|
| Home Screen Icon | ❌ | ✅ |
| Full-Screen Mode | ❌ | ✅ |
| Offline Access | Limited | Better |
| Loading Speed | Slower | Faster |
| App Drawer | ❌ | ✅ |
| Native Feel | ❌ | ✅ |

## System Requirements

- **Android Version**: 5.0 (Lollipop) or higher
- **Browser**: Chrome 40+, Firefox 44+, Samsung Internet 4.0+
- **Web engine**: No separate Android WebView/WebKit or Reown Android kit install is required—the PWA runs on the browser engine already bundled with your chosen browser
- **Storage**: ~5-10 MB for app and cache
- **Internet**: Required for initial installation and blockchain operations

## Privacy & Data

- VibeAgent PWA doesn't store private keys on your device
- Only configuration and cache data is stored locally
- All sensitive operations go through your Avocado multi-sig wallet
- You can clear data anytime by uninstalling the app

## Getting Help

If you encounter issues with the Android installation:
- Check our [GitHub Issues](https://github.com/Disseveru/vibeagent/issues)
- Join our [Discord Community](https://discord.gg/vibeagent)
- Read the main [User Guide](USER_GUIDE.md)

## Future Enhancements

We're working on adding:
- [ ] Push notifications for opportunities
- [ ] Background sync for strategy monitoring
- [ ] Share integration for exporting strategies
- [ ] Camera access for QR code scanning

---

**Ready to get started?** Visit your VibeAgent instance on your Android device and tap "Install"! 🚀
