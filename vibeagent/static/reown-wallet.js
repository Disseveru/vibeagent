/**
 * Reown AppKit Wallet Integration for VibeAgent
 * Supports 300+ wallets including MetaMask, Trust Wallet, Coinbase Wallet, Rainbow, etc.
 * Mobile-friendly with WalletConnect support
 */

// Wallet state
let walletState = {
    connected: false,
    address: null,
    chainId: null,
    balance: null,
    provider: null,
    isWalletConnect: false
};

// AppKit modal instance
let appKitModal = null;

// Network configurations
const NETWORKS = {
    ethereum: {
        chainId: 1,
        name: 'Ethereum',
        rpcUrl: 'https://eth.llamarpc.com',
        currency: 'ETH',
        explorerUrl: 'https://etherscan.io'
    },
    polygon: {
        chainId: 137,
        name: 'Polygon',
        rpcUrl: 'https://polygon-rpc.com',
        currency: 'MATIC',
        explorerUrl: 'https://polygonscan.com'
    },
    arbitrum: {
        chainId: 42161,
        name: 'Arbitrum',
        rpcUrl: 'https://arb1.arbitrum.io/rpc',
        currency: 'ETH',
        explorerUrl: 'https://arbiscan.io'
    }
};

// Safety settings
const SAFETY_SETTINGS = {
    manualApproval: true,
    minProfitUsd: 50,
    maxGasPriceGwei: 100
};

/**
 * Check if running on mobile device
 * Uses feature detection instead of user-agent sniffing for better reliability
 */
function isMobileDevice() {
    // Primary check: touch points (most reliable)
    if (navigator.maxTouchPoints > 0) {
        return true;
    }
    
    // Secondary check: coarse pointer (touch screen)
    if (window.matchMedia && window.matchMedia('(pointer: coarse)').matches) {
        return true;
    }
    
    // Fallback: user agent (less reliable but catches edge cases)
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}

/**
 * Get Reown Project ID from environment or fallback
 */
function getReownProjectId() {
    // Try to get from meta tag first (can be injected server-side)
    const metaTag = document.querySelector('meta[name="reown-project-id"]');
    if (metaTag && metaTag.content) {
        return metaTag.content;
    }
    
    // Fallback to a demo project ID (should be replaced in production)
    // Users should get their own project ID from https://cloud.reown.com/
    return 'demo-project-id-replace-me';
}

/**
 * Initialize Reown AppKit with WalletConnect support
 */
async function initReownWallet() {
    console.log('Initializing Reown Wallet integration...');
    
    // Check if running in browser
    if (typeof window === 'undefined') {
        console.error('Reown wallet requires browser environment');
        return false;
    }

    // Check for injected provider (MetaMask extension, in-app browser, etc.)
    if (typeof window.ethereum !== 'undefined') {
        console.log('Detected injected Web3 provider');
        walletState.provider = window.ethereum;
        walletState.isWalletConnect = false;
        setupEventListeners();
        return true;
    }
    
    // No injected provider - initialize WalletConnect via AppKit
    // This is common on mobile browsers
    console.log('No injected provider detected, will use WalletConnect');
    
    try {
        // Initialize AppKit modal for WalletConnect
        // Using a simple implementation that works with vanilla JS
        await initAppKitModal();
        return true;
    } catch (error) {
        console.error('Failed to initialize AppKit:', error);
        return false;
    }
}

/**
 * Initialize AppKit modal for WalletConnect
 * This creates a connection interface when no injected provider is available
 */
async function initAppKitModal() {
    const projectId = getReownProjectId();
    
    if (!projectId || projectId === 'demo-project-id-replace-me') {
        console.warn('Using demo project ID. Get your own at https://cloud.reown.com/');
    }
    
    // Check if WalletConnect Universal Provider is available
    if (typeof window.WalletConnectUniversalProvider === 'undefined') {
        console.log('WalletConnect Universal Provider not loaded, using fallback');
        return;
    }
    
    // Initialize WalletConnect Universal Provider
    try {
        const UniversalProvider = window.WalletConnectUniversalProvider.UniversalProvider;
        const provider = await UniversalProvider.init({
            projectId: projectId,
            chains: ['eip155:1', 'eip155:137', 'eip155:42161'], // Ethereum, Polygon, Arbitrum
            showQrModal: true,
            metadata: {
                name: 'VibeAgent',
                description: 'Real-time DeFi opportunity scanner',
                url: window.location.origin,
                icons: [`${window.location.origin}/static/icons/icon-192x192.png`]
            }
        });
        
        walletState.provider = provider;
        walletState.isWalletConnect = true;
        console.log('WalletConnect Universal Provider initialized');
    } catch (error) {
        console.error('Failed to initialize WalletConnect Universal Provider:', error);
    }
}

/**
 * Setup wallet event listeners for injected providers
 */
function setupEventListeners() {
    if (!walletState.provider) return;
    
    // Account changed
    walletState.provider.on('accountsChanged', (accounts) => {
        if (accounts.length === 0) {
            disconnectWallet();
        } else {
            walletState.address = accounts[0];
            updateWalletUI();
            updateBalance();
        }
    });
    
    // Chain changed
    walletState.provider.on('chainChanged', (chainId) => {
        walletState.chainId = parseInt(chainId, 16);
        updateWalletUI();
        updateBalance();
    });
}

/**
 * Setup WalletConnect event listeners
 */
function setupWalletConnectListeners() {
    if (!walletState.provider || !walletState.isWalletConnect) return;
    
    // Session update (account or chain changed)
    walletState.provider.on('session_update', ({ topic, params }) => {
        const { namespaces } = params;
        const session = walletState.provider.session;
        
        if (session && session.namespaces && session.namespaces.eip155) {
            const accounts = session.namespaces.eip155.accounts;
            if (accounts.length > 0) {
                const accountStr = accounts[0];
                const address = accountStr.split(':')[2];
                const chainId = parseInt(accountStr.split(':')[1], 10);
                
                walletState.address = address;
                walletState.chainId = chainId;
                updateWalletUI();
                updateBalance();
            }
        }
    });
    
    // Session delete (disconnection)
    walletState.provider.on('session_delete', () => {
        disconnectWallet();
    });
    
    // Display URI for manual connection
    walletState.provider.on('display_uri', (uri) => {
        console.log('WalletConnect URI:', uri);
        // Could show QR code or deep link here
    });
}

/**
 * Connect wallet (supports both injected providers and WalletConnect)
 */
async function connectWallet() {
    try {
        // Initialize if not already done
        if (!walletState.provider) {
            const initialized = await initReownWallet();
            
            // If initialization failed and still no provider
            if (!initialized && !walletState.provider) {
                const isMobile = isMobileDevice();
                let message;
                
                if (isMobile) {
                    // On mobile, guide user to use WalletConnect or MetaMask app
                    message = 'To connect on mobile: Open this page in MetaMask app browser, or install a wallet that supports WalletConnect. WalletConnect libraries are not available in this environment.';
                } else {
                    // On desktop, suggest installing MetaMask
                    message = 'Please install MetaMask or another Web3 wallet extension. WalletConnect is not available in this environment.';
                }
                
                showWalletStatus(message, 'error');
                return false;
            }
        }
        
        // If still no provider, show error
        if (!walletState.provider) {
            const isMobile = isMobileDevice();
            let message;
            
            if (isMobile) {
                message = 'To connect on mobile: Open this page in MetaMask app browser, or use a wallet that supports WalletConnect';
            } else {
                message = 'Please install MetaMask or another Web3 wallet extension';
            }
            
            showWalletStatus(message, 'error');
            return false;
        }
        
        // Handle WalletConnect provider
        if (walletState.isWalletConnect) {
            return await connectWalletConnect();
        }
        
        // Handle injected provider (MetaMask, etc.)
        return await connectInjectedProvider();
        
    } catch (error) {
        console.error('Error connecting wallet:', error);
        showWalletStatus(`Error connecting wallet: ${error.message}`, 'error');
        return false;
    }
}

/**
 * Connect using injected provider (MetaMask extension, in-app browser, etc.)
 */
async function connectInjectedProvider() {
    try {
        // Request account access
        const accounts = await walletState.provider.request({
            method: 'eth_requestAccounts'
        });
        
        if (accounts.length === 0) {
            showWalletStatus('No accounts found', 'error');
            return false;
        }
        
        walletState.connected = true;
        walletState.address = accounts[0];
        
        // Get chain ID
        const chainId = await walletState.provider.request({
            method: 'eth_chainId'
        });
        walletState.chainId = parseInt(chainId, 16);
        
        // Update UI
        updateWalletUI();
        await updateBalance();
        
        // Notify backend
        await notifyBackendWalletConnected();
        
        showWalletStatus('Wallet connected successfully!', 'success');
        return true;
        
    } catch (error) {
        console.error('Error connecting injected provider:', error);
        
        // User rejected the connection
        if (error.code === 4001) {
            showWalletStatus('Connection rejected by user', 'error');
        } else {
            showWalletStatus(`Error connecting: ${error.message}`, 'error');
        }
        return false;
    }
}

/**
 * Connect using WalletConnect
 */
async function connectWalletConnect() {
    try {
        // Connect the provider (this shows QR modal or opens app)
        await walletState.provider.connect({
            namespaces: {
                eip155: {
                    methods: [
                        'eth_sendTransaction',
                        'eth_signTransaction',
                        'eth_sign',
                        'personal_sign',
                        'eth_signTypedData'
                    ],
                    chains: ['eip155:1', 'eip155:137', 'eip155:42161'],
                    events: ['chainChanged', 'accountsChanged'],
                    rpcMap: {
                        1: 'https://eth.llamarpc.com',
                        137: 'https://polygon-rpc.com',
                        42161: 'https://arb1.arbitrum.io/rpc'
                    }
                }
            }
        });
        
        // Get accounts from session
        const session = walletState.provider.session;
        if (!session || !session.namespaces || !session.namespaces.eip155) {
            showWalletStatus('No accounts found in session', 'error');
            return false;
        }
        
        const accounts = session.namespaces.eip155.accounts;
        if (accounts.length === 0) {
            showWalletStatus('No accounts found', 'error');
            return false;
        }
        
        // Parse account (format: "eip155:1:0x...")
        const accountStr = accounts[0];
        const address = accountStr.split(':')[2];
        
        walletState.connected = true;
        walletState.address = address;
        
        // Parse chain ID from account
        const chainId = parseInt(accountStr.split(':')[1], 10);
        walletState.chainId = chainId;
        
        // Setup WalletConnect event listeners
        setupWalletConnectListeners();
        
        // Update UI
        updateWalletUI();
        await updateBalance();
        
        // Notify backend
        await notifyBackendWalletConnected();
        
        showWalletStatus('Wallet connected via WalletConnect!', 'success');
        return true;
        
    } catch (error) {
        console.error('Error connecting WalletConnect:', error);
        
        // User rejected the connection
        if (error.message && error.message.includes('User rejected')) {
            showWalletStatus('Connection rejected by user', 'error');
        } else {
            showWalletStatus(`WalletConnect error: ${error.message}`, 'error');
        }
        return false;
    }
}

/**
 * Create WalletConnect URI for deep linking
 */
async function createWalletConnectUri() {
    // This would be implemented with actual WalletConnect SDK
    // For now, return null as we'll rely on the modal
    return null;
}

/**
 * Disconnect wallet
 */
async function disconnectWallet() {
    // Disconnect WalletConnect session if active
    if (walletState.isWalletConnect && walletState.provider) {
        try {
            await walletState.provider.disconnect();
        } catch (error) {
            console.error('Error disconnecting WalletConnect:', error);
        }
    }
    
    walletState.connected = false;
    walletState.address = null;
    walletState.chainId = null;
    walletState.balance = null;
    walletState.isWalletConnect = false;
    
    updateWalletUI();
    showWalletStatus('Wallet disconnected', 'info');
}

/**
 * Switch network
 */
async function switchNetwork(networkName) {
    const network = NETWORKS[networkName];
    if (!network) {
        showWalletStatus(`Unknown network: ${networkName}`, 'error');
        return false;
    }
    
    try {
        await walletState.provider.request({
            method: 'wallet_switchEthereumChain',
            params: [{ chainId: `0x${network.chainId.toString(16)}` }]
        });
        
        showWalletStatus(`Switched to ${network.name}`, 'success');
        return true;
        
    } catch (error) {
        // Chain not added, try to add it
        if (error.code === 4902) {
            try {
                await walletState.provider.request({
                    method: 'wallet_addEthereumChain',
                    params: [{
                        chainId: `0x${network.chainId.toString(16)}`,
                        chainName: network.name,
                        nativeCurrency: {
                            name: network.currency,
                            symbol: network.currency,
                            decimals: 18
                        },
                        rpcUrls: [network.rpcUrl],
                        blockExplorerUrls: [network.explorerUrl]
                    }]
                });
                
                showWalletStatus(`Added and switched to ${network.name}`, 'success');
                return true;
                
            } catch (addError) {
                console.error('Error adding network:', addError);
                showWalletStatus(`Error adding network: ${addError.message}`, 'error');
                return false;
            }
        }
        
        console.error('Error switching network:', error);
        showWalletStatus(`Error switching network: ${error.message}`, 'error');
        return false;
    }
}

/**
 * Update wallet balance
 */
async function updateBalance() {
    if (!walletState.connected || !walletState.address) {
        return;
    }
    
    try {
        let balance;
        
        if (walletState.isWalletConnect) {
            // WalletConnect uses EIP-155 request format
            balance = await walletState.provider.request({
                method: 'eth_getBalance',
                params: [walletState.address, 'latest']
            }, `eip155:${walletState.chainId}`);
        } else {
            // Injected provider uses standard format
            balance = await walletState.provider.request({
                method: 'eth_getBalance',
                params: [walletState.address, 'latest']
            });
        }
        
        // Convert from Wei to Ether (using BigInt for precision)
        const balanceWei = BigInt(balance);
        const etherDivisor = BigInt(1e18);
        const etherBalance = Number(balanceWei) / Number(etherDivisor);
        
        walletState.balance = etherBalance;
        updateWalletUI();
        
    } catch (error) {
        console.error('Error fetching balance:', error);
    }
}

/**
 * Update wallet UI
 */
function updateWalletUI() {
    const walletInfoDiv = document.getElementById('walletInfo');
    const connectBtn = document.getElementById('connectWalletBtn');
    const disconnectBtn = document.getElementById('disconnectWalletBtn');
    
    if (!walletInfoDiv) return;
    
    if (walletState.connected) {
        // Show wallet info
        const networkName = Object.keys(NETWORKS).find(
            key => NETWORKS[key].chainId === walletState.chainId
        ) || 'Unknown';
        
        const network = NETWORKS[networkName] || {};
        
        walletInfoDiv.innerHTML = `
            <div class="wallet-connected">
                <div class="wallet-address">
                    <strong>Connected:</strong> 
                    <span class="address">${formatAddress(walletState.address)}</span>
                    <button onclick="copyAddress()" class="copy-btn" title="Copy address">📋</button>
                </div>
                <div class="wallet-balance">
                    <strong>Balance:</strong> 
                    <span class="balance">${formatBalance(walletState.balance)} ${network.currency || 'ETH'}</span>
                    <button onclick="updateBalance()" class="refresh-btn" title="Refresh balance">🔄</button>
                </div>
                <div class="wallet-network">
                    <strong>Network:</strong> 
                    <span class="network">${network.name || 'Unknown'}</span>
                </div>
            </div>
        `;
        
        if (connectBtn) connectBtn.style.display = 'none';
        if (disconnectBtn) disconnectBtn.style.display = 'inline-block';
        
    } else {
        // Show connect button
        walletInfoDiv.innerHTML = `
            <div class="wallet-disconnected">
                <p>Connect your wallet to start using VibeAgent</p>
                <p class="wallet-info-text">
                    Supports 300+ wallets including MetaMask, Trust Wallet, Coinbase Wallet, Rainbow, and more
                </p>
            </div>
        `;
        
        if (connectBtn) connectBtn.style.display = 'inline-block';
        if (disconnectBtn) disconnectBtn.style.display = 'none';
    }
}

/**
 * Format wallet address
 */
function formatAddress(address) {
    if (!address) return '';
    return `${address.substring(0, 6)}...${address.substring(address.length - 4)}`;
}

/**
 * Format balance
 */
function formatBalance(balance) {
    if (balance === null || balance === undefined) return '0.0000';
    return balance.toFixed(4);
}

/**
 * Copy address to clipboard
 */
function copyAddress() {
    if (!walletState.address) return;
    
    navigator.clipboard.writeText(walletState.address).then(() => {
        showWalletStatus('Address copied to clipboard!', 'success');
    }).catch(err => {
        console.error('Failed to copy address:', err);
        showWalletStatus('Failed to copy address', 'error');
    });
}

/**
 * Show wallet status message
 */
function showWalletStatus(message, type = 'info') {
    // Try to write to landing page status first
    const connectStatus = document.getElementById('connectStatus');
    if (connectStatus && !connectStatus.classList.contains('hidden')) {
        connectStatus.textContent = message;
        connectStatus.classList.remove('info', 'success', 'error');
        connectStatus.classList.add(type);
        return;
    }
    
    // Otherwise use wallet status in main app
    const statusDiv = document.getElementById('walletStatus');
    if (statusDiv) {
        statusDiv.textContent = message;
        statusDiv.className = `status-message status-${type}`;
        statusDiv.style.display = 'block';
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            statusDiv.style.display = 'none';
        }, 5000);
        return;
    }
    
    // Fallback to main status if nothing else works
    if (typeof showStatus === 'function') {
        showStatus(message, type);
    }
}

/**
 * Notify backend of wallet connection
 */
async function notifyBackendWalletConnected() {
    try {
        const response = await fetch('/api/wallet/connect', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                address: walletState.address,
                chainId: walletState.chainId
            })
        });
        
        if (!response.ok) {
            console.warn('Failed to notify backend of wallet connection');
        }
    } catch (error) {
        console.error('Error notifying backend:', error);
    }
}

/**
 * Get explorer URL for transaction
 */
function getExplorerUrl(txHash, networkName) {
    const network = NETWORKS[networkName];
    if (!network) return '#';
    return `${network.explorerUrl}/tx/${txHash}`;
}

/**
 * Execute transaction with safety checks
 */
async function executeTransaction(txParams) {
    // Safety checks
    if (SAFETY_SETTINGS.manualApproval) {
        const confirmed = confirm(
            `Execute transaction?\n\n` +
            `To: ${txParams.to}\n` +
            `Value: ${txParams.value || '0'} ETH\n` +
            `Gas Limit: ${txParams.gas || 'auto'}\n\n` +
            `Make sure you understand this transaction before proceeding.`
        );
        
        if (!confirmed) {
            return { success: false, error: 'Transaction cancelled by user' };
        }
    }
    
    try {
        const txHash = await walletState.provider.request({
            method: 'eth_sendTransaction',
            params: [txParams]
        });
        
        return { success: true, txHash };
        
    } catch (error) {
        console.error('Transaction error:', error);
        return { success: false, error: error.message };
    }
}

/**
 * Update safety settings
 */
function updateSafetySettings(settings) {
    Object.assign(SAFETY_SETTINGS, settings);
    console.log('Safety settings updated:', SAFETY_SETTINGS);
}

/**
 * Get wallet state (for debugging and backend sync)
 */
function getWalletState() {
    return { ...walletState };
}

// Initialize on page load
if (typeof window !== 'undefined') {
    window.addEventListener('DOMContentLoaded', () => {
        initReownWallet();
        updateWalletUI();
    });
}

// Export functions for global use
if (typeof window !== 'undefined') {
    window.connectWallet = connectWallet;
    window.disconnectWallet = disconnectWallet;
    window.switchNetwork = switchNetwork;
    window.updateBalance = updateBalance;
    window.copyAddress = copyAddress;
    window.getExplorerUrl = getExplorerUrl;
    window.executeTransaction = executeTransaction;
    window.updateSafetySettings = updateSafetySettings;
    window.getWalletState = getWalletState;
}
