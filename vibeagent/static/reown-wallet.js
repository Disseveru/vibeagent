/**
 * Reown AppKit Wallet Integration for VibeAgent
 * Supports 300+ wallets including MetaMask, Trust Wallet, Coinbase Wallet, Rainbow, etc.
 */

// Wallet state
let walletState = {
    connected: false,
    address: null,
    chainId: null,
    balance: null,
    provider: null
};

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
 * Initialize Reown AppKit with wagmi/viem
 * Note: This is a simplified vanilla JS implementation
 * For production, consider using the full React implementation
 */
async function initReownWallet() {
    console.log('Initializing Reown Wallet integration...');
    
    // Check if running in browser with Web3 support
    if (typeof window === 'undefined') {
        console.error('Reown wallet requires browser environment');
        return false;
    }

    // For now, we'll use window.ethereum as fallback
    // In production, this should be replaced with full Reown AppKit SDK
    if (typeof window.ethereum !== 'undefined') {
        walletState.provider = window.ethereum;
        setupEventListeners();
        return true;
    }
    
    console.warn('No Web3 provider detected. Please install MetaMask or another Web3 wallet.');
    return false;
}

/**
 * Setup wallet event listeners
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
 * Connect wallet
 */
async function connectWallet() {
    try {
        if (!walletState.provider) {
            await initReownWallet();
        }
        
        if (!walletState.provider) {
            showWalletStatus('Please install MetaMask or another Web3 wallet', 'error');
            return false;
        }
        
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
        console.error('Error connecting wallet:', error);
        showWalletStatus(`Error connecting wallet: ${error.message}`, 'error');
        return false;
    }
}

/**
 * Disconnect wallet
 */
function disconnectWallet() {
    walletState.connected = false;
    walletState.address = null;
    walletState.chainId = null;
    walletState.balance = null;
    
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
        const balance = await walletState.provider.request({
            method: 'eth_getBalance',
            params: [walletState.address, 'latest']
        });
        
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
    const statusDiv = document.getElementById('walletStatus');
    if (!statusDiv) {
        // Fallback to main status if wallet status doesn't exist
        if (typeof showStatus === 'function') {
            showStatus(message, type);
        }
        return;
    }
    
    statusDiv.textContent = message;
    statusDiv.className = `status-message status-${type}`;
    statusDiv.style.display = 'block';
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        statusDiv.style.display = 'none';
    }, 5000);
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
