/**
 * Simple Web3 Wallet Integration for VibeAgent
 * Supports MetaMask and other injected providers (window.ethereum)
 * No external dependencies - pure Web3
 */

let walletState = {
    connected: false,
    address: null,
    chainId: null,
    balance: null
};

// Network configurations
const NETWORKS = {
    1: { name: 'Ethereum', currency: 'ETH', explorerUrl: 'https://etherscan.io' },
    137: { name: 'Polygon', currency: 'MATIC', explorerUrl: 'https://polygonscan.com' },
    42161: { name: 'Arbitrum', currency: 'ETH', explorerUrl: 'https://arbiscan.io' }
};

/**
 * Check if Web3 wallet is available
 */
function isWalletAvailable() {
    return typeof window.ethereum !== 'undefined';
}

/**
 * Connect wallet
 */
async function connectWallet() {
    if (!isWalletAvailable()) {
        console.error('No Web3 wallet found. Please install MetaMask.');
        return false;
    }

    try {
        // Request account access
        const accounts = await window.ethereum.request({ 
            method: 'eth_requestAccounts' 
        });
        
        if (accounts.length === 0) {
            console.error('No accounts found');
            return false;
        }

        walletState.address = accounts[0];
        walletState.connected = true;

        // Get chain ID
        const chainId = await window.ethereum.request({ 
            method: 'eth_chainId' 
        });
        walletState.chainId = parseInt(chainId, 16);

        // Get balance
        await updateBalance();

        // Setup listeners
        setupListeners();

        console.log('Wallet connected:', walletState.address);
        return true;

    } catch (error) {
        console.error('Failed to connect wallet:', error);
        return false;
    }
}

/**
 * Disconnect wallet
 */
async function disconnectWallet() {
    walletState.connected = false;
    walletState.address = null;
    walletState.chainId = null;
    walletState.balance = null;
    console.log('Wallet disconnected');
}

/**
 * Update wallet balance
 */
async function updateBalance() {
    if (!walletState.connected || !walletState.address) {
        return;
    }

    try {
        const balance = await window.ethereum.request({
            method: 'eth_getBalance',
            params: [walletState.address, 'latest']
        });

        // Convert from wei to ether
        walletState.balance = parseInt(balance, 16) / 1e18;
        
        return walletState.balance;
    } catch (error) {
        console.error('Failed to get balance:', error);
        return null;
    }
}

/**
 * Switch network
 */
async function switchNetwork(chainId) {
    if (!isWalletAvailable()) {
        return false;
    }

    try {
        await window.ethereum.request({
            method: 'wallet_switchEthereumChain',
            params: [{ chainId: `0x${chainId.toString(16)}` }],
        });
        
        walletState.chainId = chainId;
        await updateBalance();
        return true;
    } catch (error) {
        console.error('Failed to switch network:', error);
        return false;
    }
}

/**
 * Setup event listeners
 */
function setupListeners() {
    if (!window.ethereum) return;

    // Account changed
    window.ethereum.on('accountsChanged', (accounts) => {
        if (accounts.length === 0) {
            disconnectWallet();
        } else {
            walletState.address = accounts[0];
            updateBalance();
        }
    });

    // Chain changed
    window.ethereum.on('chainChanged', (chainId) => {
        walletState.chainId = parseInt(chainId, 16);
        updateBalance();
    });
}

/**
 * Get wallet state
 */
function getWalletState() {
    return { ...walletState };
}

/**
 * Format address
 */
function formatAddress(address) {
    if (!address) return '';
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
}

/**
 * Format balance
 */
function formatBalance(balance) {
    if (balance === null || balance === undefined) return '0.0';
    return balance.toFixed(4);
}

/**
 * Get network name
 */
function getNetworkName(chainId) {
    return NETWORKS[chainId]?.name || `Chain ${chainId}`;
}

/**
 * Execute transaction
 */
async function executeTransaction(txParams) {
    if (!walletState.connected) {
        throw new Error('Wallet not connected');
    }

    try {
        const txHash = await window.ethereum.request({
            method: 'eth_sendTransaction',
            params: [txParams],
        });
        
        return txHash;
    } catch (error) {
        console.error('Transaction failed:', error);
        throw error;
    }
}

// Export functions for global access
window.connectWallet = connectWallet;
window.disconnectWallet = disconnectWallet;
window.updateBalance = updateBalance;
window.switchNetwork = switchNetwork;
window.getWalletState = getWalletState;
window.formatAddress = formatAddress;
window.formatBalance = formatBalance;
window.getNetworkName = getNetworkName;
window.executeTransaction = executeTransaction;
window.isWalletAvailable = isWalletAvailable;
