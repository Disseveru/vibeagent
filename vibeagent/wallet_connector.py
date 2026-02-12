"""
WalletConnect (Reown) Integration for VibeAgent
Allows any wallet to connect and perform autonomous arbitrage transactions
"""
import os
from typing import Dict, List, Optional, Any, Callable
from web3 import Web3
from eth_account.signers.local import LocalAccount
import json
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class WalletConnector:
    """
    Manages WalletConnect integration for secure wallet connections
    Supports Ethereum, Polygon, and Arbitrum networks
    """
    
    # Supported networks with chain IDs
    SUPPORTED_NETWORKS = {
        "ethereum": {
            "chain_id": 1,
            "name": "Ethereum Mainnet",
            "rpc_url_key": "ETHEREUM_RPC_URL",
            "native_token": "ETH"
        },
        "polygon": {
            "chain_id": 137,
            "name": "Polygon",
            "rpc_url_key": "POLYGON_RPC_URL",
            "native_token": "MATIC"
        },
        "arbitrum": {
            "chain_id": 42161,
            "name": "Arbitrum One",
            "rpc_url_key": "ARBITRUM_RPC_URL",
            "native_token": "ETH"
        }
    }
    
    def __init__(self, network: str = "ethereum"):
        """
        Initialize WalletConnect integration
        
        Args:
            network: Network name (ethereum, polygon, arbitrum)
        """
        if network not in self.SUPPORTED_NETWORKS:
            raise ValueError(f"Unsupported network: {network}. Supported: {list(self.SUPPORTED_NETWORKS.keys())}")
        
        self.network = network
        self.network_info = self.SUPPORTED_NETWORKS[network]
        self.chain_id = self.network_info["chain_id"]
        
        # Initialize Web3 connection
        rpc_url = os.getenv(self.network_info["rpc_url_key"])
        if not rpc_url:
            raise ValueError(f"RPC URL not configured for {network}. Set {self.network_info['rpc_url_key']} in .env")
        
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        
        # Connection state
        self.connected = False
        self.wallet_address: Optional[str] = None
        self.session_data: Dict[str, Any] = {}
        self.connection_timestamp: Optional[float] = None
        
        # For browser-based WalletConnect, we'll use a session-based approach
        # The actual signing happens in the browser via WalletConnect modal
        self.pending_requests: Dict[str, Dict] = {}
        
    def connect_wallet(self, wallet_address: str) -> Dict[str, Any]:
        """
        Connect a wallet (called after user connects via WalletConnect in browser)
        
        Args:
            wallet_address: User's wallet address from WalletConnect
            
        Returns:
            Connection status and wallet info
        """
        try:
            # Validate address format
            wallet_address = Web3.to_checksum_address(wallet_address)
            
            # Verify network
            if not self.web3.is_connected():
                raise ConnectionError("Failed to connect to blockchain RPC")
            
            # Store connection info
            self.wallet_address = wallet_address
            self.connected = True
            self.connection_timestamp = time.time()
            
            # Get wallet balance
            balance_wei = self.web3.eth.get_balance(wallet_address)
            balance = self.web3.from_wei(balance_wei, 'ether')
            
            self.session_data = {
                "address": wallet_address,
                "network": self.network,
                "chain_id": self.chain_id,
                "balance": float(balance),
                "native_token": self.network_info["native_token"],
                "connected_at": datetime.fromtimestamp(self.connection_timestamp).isoformat()
            }
            
            print(f"✓ Wallet connected: {wallet_address}")
            print(f"  Network: {self.network_info['name']}")
            print(f"  Balance: {balance:.4f} {self.network_info['native_token']}")
            
            return {
                "success": True,
                "wallet_address": wallet_address,
                "network": self.network,
                "chain_id": self.chain_id,
                "balance": float(balance),
                "native_token": self.network_info["native_token"]
            }
            
        except Exception as e:
            print(f"Error connecting wallet: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def disconnect_wallet(self) -> Dict[str, Any]:
        """
        Disconnect the wallet
        
        Returns:
            Disconnection status
        """
        try:
            self.connected = False
            self.wallet_address = None
            self.session_data = {}
            self.connection_timestamp = None
            self.pending_requests = {}
            
            print("✓ Wallet disconnected")
            
            return {
                "success": True,
                "message": "Wallet disconnected successfully"
            }
            
        except Exception as e:
            print(f"Error disconnecting wallet: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_connection_status(self) -> Dict[str, Any]:
        """
        Get current connection status
        
        Returns:
            Connection status information
        """
        if not self.connected:
            return {
                "connected": False,
                "network": self.network,
                "chain_id": self.chain_id
            }
        
        # Update balance
        if self.wallet_address:
            try:
                balance_wei = self.web3.eth.get_balance(self.wallet_address)
                balance = self.web3.from_wei(balance_wei, 'ether')
                self.session_data["balance"] = float(balance)
            except Exception as e:
                print(f"Error updating balance: {e}")
        
        return {
            "connected": True,
            **self.session_data
        }
    
    def check_gas_balance(self, estimated_gas_units: int = 500000) -> Dict[str, Any]:
        """
        Check if wallet has sufficient gas balance for transaction
        
        Args:
            estimated_gas_units: Estimated gas units for transaction
            
        Returns:
            Gas check results with recommendations
        """
        if not self.connected or not self.wallet_address:
            return {
                "sufficient": False,
                "error": "Wallet not connected"
            }
        
        try:
            # Get current gas price
            gas_price = self.web3.eth.gas_price
            gas_price_gwei = self.web3.from_wei(gas_price, 'gwei')
            
            # Calculate required ETH for gas
            gas_cost_wei = gas_price * estimated_gas_units
            gas_cost_eth = self.web3.from_wei(gas_cost_wei, 'ether')
            
            # Get wallet balance
            balance_wei = self.web3.eth.get_balance(self.wallet_address)
            balance_eth = self.web3.from_wei(balance_wei, 'ether')
            
            # Add 20% buffer for gas price fluctuations
            recommended_balance = gas_cost_eth * 1.2
            sufficient = balance_eth >= recommended_balance
            
            # Get max gas price limit from config
            max_gas_gwei = float(os.getenv("MAX_GAS_PRICE_GWEI", "100"))
            gas_price_acceptable = gas_price_gwei <= max_gas_gwei
            
            result = {
                "sufficient": sufficient and gas_price_acceptable,
                "current_balance": float(balance_eth),
                "required_gas": float(gas_cost_eth),
                "recommended_balance": float(recommended_balance),
                "current_gas_price_gwei": float(gas_price_gwei),
                "max_gas_price_gwei": max_gas_gwei,
                "gas_price_acceptable": gas_price_acceptable,
                "native_token": self.network_info["native_token"],
                "estimated_gas_units": estimated_gas_units
            }
            
            if not sufficient:
                result["warning"] = f"Insufficient balance. Need at least {recommended_balance:.6f} {self.network_info['native_token']}"
            
            if not gas_price_acceptable:
                result["warning"] = f"Gas price too high: {gas_price_gwei:.2f} Gwei (max: {max_gas_gwei} Gwei)"
            
            return result
            
        except Exception as e:
            print(f"Error checking gas balance: {e}")
            return {
                "sufficient": False,
                "error": str(e)
            }
    
    def validate_network(self, required_network: str) -> bool:
        """
        Validate that current network matches required network
        
        Args:
            required_network: Required network name
            
        Returns:
            True if network matches, False otherwise
        """
        return self.network.lower() == required_network.lower()
    
    def switch_network(self, network: str) -> Dict[str, Any]:
        """
        Switch to a different network
        
        Args:
            network: Target network name
            
        Returns:
            Switch status
        """
        if network not in self.SUPPORTED_NETWORKS:
            return {
                "success": False,
                "error": f"Unsupported network: {network}"
            }
        
        try:
            # Store old connection state
            was_connected = self.connected
            old_address = self.wallet_address
            
            # Reinitialize with new network using dedicated method
            self._reinitialize(network)
            
            # If was connected, attempt to reconnect with same address
            if was_connected and old_address:
                return self.connect_wallet(old_address)
            
            return {
                "success": True,
                "network": network,
                "chain_id": self.SUPPORTED_NETWORKS[network]["chain_id"]
            }
            
        except Exception as e:
            print(f"Error switching network: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _reinitialize(self, network: str):
        """
        Reinitialize the connector with a new network
        
        Args:
            network: Network name to switch to
        """
        self.network = network
        self.network_info = self.SUPPORTED_NETWORKS[network]
        self.chain_id = self.network_info["chain_id"]
        
        # Reinitialize Web3 connection
        rpc_url = os.getenv(self.network_info["rpc_url_key"])
        if not rpc_url:
            raise ValueError(f"RPC URL not configured for {network}. Set {self.network_info['rpc_url_key']} in .env")
        
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        
        # Reset connection state
        self.connected = False
        self.wallet_address = None
        self.session_data = {}
        self.connection_timestamp = None
        self.pending_requests = {}
    
    def create_transaction_request(
        self,
        to: str,
        data: str,
        value: int = 0,
        gas_limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create a transaction request for WalletConnect signing
        
        Args:
            to: Target contract address
            data: Encoded transaction data
            value: ETH value to send (in wei)
            gas_limit: Optional gas limit
            
        Returns:
            Transaction request dict
        """
        if not self.connected or not self.wallet_address:
            raise ValueError("Wallet not connected")
        
        try:
            # Get nonce
            nonce = self.web3.eth.get_transaction_count(self.wallet_address)
            
            # Get gas price
            gas_price = self.web3.eth.gas_price
            
            # Estimate gas if not provided
            if gas_limit is None:
                try:
                    gas_limit = self.web3.eth.estimate_gas({
                        'from': self.wallet_address,
                        'to': to,
                        'data': data,
                        'value': value
                    })
                    # Add 20% buffer
                    gas_limit = int(gas_limit * 1.2)
                except Exception as e:
                    print(f"Gas estimation failed: {e}, using default")
                    gas_limit = 500000
            
            # Build transaction
            transaction = {
                'from': self.wallet_address,
                'to': to,
                'value': value,
                'gas': gas_limit,
                'gasPrice': gas_price,
                'nonce': nonce,
                'data': data,
                'chainId': self.chain_id
            }
            
            # Generate request ID
            request_id = f"tx_{int(time.time())}_{len(self.pending_requests)}"
            
            # Store pending request
            self.pending_requests[request_id] = {
                'transaction': transaction,
                'created_at': time.time(),
                'status': 'pending'
            }
            
            return {
                "success": True,
                "request_id": request_id,
                "transaction": transaction
            }
            
        except Exception as e:
            print(f"Error creating transaction request: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_pending_request(self, request_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a pending transaction request
        
        Args:
            request_id: Request ID
            
        Returns:
            Request data or None
        """
        return self.pending_requests.get(request_id)
    
    def mark_request_completed(self, request_id: str, tx_hash: str):
        """
        Mark a transaction request as completed
        
        Args:
            request_id: Request ID
            tx_hash: Transaction hash
        """
        if request_id in self.pending_requests:
            self.pending_requests[request_id]['status'] = 'completed'
            self.pending_requests[request_id]['tx_hash'] = tx_hash
            self.pending_requests[request_id]['completed_at'] = time.time()
    
    def mark_request_failed(self, request_id: str, error: str):
        """
        Mark a transaction request as failed
        
        Args:
            request_id: Request ID
            error: Error message
        """
        if request_id in self.pending_requests:
            self.pending_requests[request_id]['status'] = 'failed'
            self.pending_requests[request_id]['error'] = error
            self.pending_requests[request_id]['failed_at'] = time.time()
    
    def wait_for_transaction(self, tx_hash: str, timeout: int = 300) -> Dict[str, Any]:
        """
        Wait for transaction confirmation
        
        Args:
            tx_hash: Transaction hash
            timeout: Timeout in seconds
            
        Returns:
            Transaction receipt
        """
        try:
            print(f"Waiting for transaction {tx_hash}...")
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)
            
            success = receipt['status'] == 1
            
            result = {
                "success": success,
                "tx_hash": tx_hash,
                "block_number": receipt['blockNumber'],
                "gas_used": receipt['gasUsed'],
                "status": "confirmed" if success else "failed"
            }
            
            if success:
                print(f"✓ Transaction confirmed: {tx_hash}")
            else:
                print(f"✗ Transaction failed: {tx_hash}")
            
            return result
            
        except Exception as e:
            print(f"Error waiting for transaction: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_supported_networks(self) -> List[Dict[str, Any]]:
        """
        Get list of supported networks
        
        Returns:
            List of network information
        """
        return [
            {
                "id": network_id,
                "name": info["name"],
                "chain_id": info["chain_id"],
                "native_token": info["native_token"]
            }
            for network_id, info in self.SUPPORTED_NETWORKS.items()
        ]
