"""
Instadapp Avocado Multi-Sig Wallet Integration
Converts strategies into Avocado-compatible transaction batches
"""
import os
from typing import Dict, List, Any, Optional
from web3 import Web3
from eth_account import Account
import json


class AvocadoIntegration:
    """
    Integration with Instadapp Avocado Multi-Sig Wallet
    Formats transactions for the Avocado transaction builder
    """
    
    # Avocado Multisig ABI (simplified for transaction building)
    AVOCADO_ABI = [
        {
            "name": "cast",
            "type": "function",
            "inputs": [
                {
                    "name": "actions",
                    "type": "tuple[]",
                    "components": [
                        {"name": "target", "type": "address"},
                        {"name": "data", "type": "bytes"},
                        {"name": "value", "type": "uint256"},
                        {"name": "operation", "type": "uint8"}
                    ]
                },
                {"name": "id", "type": "uint256"}
            ]
        }
    ]
    
    # Protocol addresses on different networks
    PROTOCOL_ADDRESSES = {
        "ethereum": {
            "aave_v3_pool": "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2",
            "uniswap_v3_router": "0xE592427A0AEce92De3Edee1F18E0157C05861564",
            "sushiswap_router": "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F",
        },
        "polygon": {
            "aave_v3_pool": "0x794a61358D6845594F94dc1DB02A252b5b4814aD",
            "uniswap_v3_router": "0xE592427A0AEce92De3Edee1F18E0157C05861564",
            "quickswap_router": "0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff",
        },
        "arbitrum": {
            "aave_v3_pool": "0x794a61358D6845594F94dc1DB02A252b5b4814aD",
            "uniswap_v3_router": "0xE592427A0AEce92De3Edee1F18E0157C05861564",
            "sushiswap_router": "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506",
        }
    }
    
    def __init__(self, wallet_address: str, network: str = "ethereum"):
        """
        Initialize Avocado integration
        
        Args:
            wallet_address: Avocado multi-sig wallet address
            network: Network to operate on
        """
        self.wallet_address = Web3.to_checksum_address(wallet_address)
        self.network = network
        self.web3 = Web3()
        
    def strategy_to_avocado_transactions(
        self,
        strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Convert a VibeAgent strategy into Avocado transaction builder format
        
        Args:
            strategy: Strategy dictionary from VibeAgent
            
        Returns:
            Avocado-compatible transaction batch
        """
        steps = strategy.get("steps", [])
        actions = []
        
        for step in steps:
            action = self._convert_step_to_action(step)
            if action:
                actions.append(action)
        
        # Build the transaction batch for Avocado
        return {
            "version": "1.0",
            "chainId": self._get_chain_id(self.network),
            "meta": {
                "name": f"{strategy.get('type', 'Strategy')} Execution",
                "description": f"Automated {strategy.get('type')} strategy",
                "createdBy": "VibeAgent"
            },
            "transactions": actions
        }
    
    def _convert_step_to_action(self, step: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Convert a strategy step into an Avocado action"""
        action_type = step.get("action")
        
        if action_type == "flash_loan":
            return self._build_flash_loan_action(step)
        elif action_type == "swap":
            return self._build_swap_action(step)
        elif action_type == "liquidate":
            return self._build_liquidation_action(step)
        elif action_type == "repay_flash_loan":
            # Usually handled in the flash loan callback
            return None
        
        return None
    
    def _build_flash_loan_action(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Build flash loan action for Avocado"""
        protocol = step.get("protocol", "aave_v3")
        token = step.get("token")
        amount = step.get("amount", "auto")
        
        # Get protocol address
        pool_address = self.PROTOCOL_ADDRESSES[self.network].get(f"{protocol}_pool")
        
        return {
            "to": pool_address,
            "value": "0",
            "data": None,  # Would be encoded function call
            "operation": 0,  # CALL operation
            "description": f"Flash loan from {protocol}",
            "meta": {
                "protocol": protocol,
                "token": token,
                "amount": amount
            }
        }
    
    def _build_swap_action(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Build swap action for Avocado"""
        dex = step.get("dex", "uniswap_v3")
        from_token = step.get("from")
        to_token = step.get("to")
        
        # Get DEX router address
        router_address = self.PROTOCOL_ADDRESSES[self.network].get(f"{dex}_router")
        
        return {
            "to": router_address,
            "value": "0",
            "data": None,  # Would be encoded swap function call
            "operation": 0,
            "description": f"Swap on {dex}",
            "meta": {
                "dex": dex,
                "fromToken": from_token,
                "toToken": to_token
            }
        }
    
    def _build_liquidation_action(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Build liquidation action for Avocado"""
        protocol = step.get("protocol")
        account = step.get("account")
        collateral_token = step.get("collateral_token")
        debt_token = step.get("debt_token")
        
        # Get protocol address
        pool_address = self.PROTOCOL_ADDRESSES[self.network].get(f"{protocol}_pool")
        
        return {
            "to": pool_address,
            "value": "0",
            "data": None,  # Would be encoded liquidation call
            "operation": 0,
            "description": f"Liquidate on {protocol}",
            "meta": {
                "protocol": protocol,
                "account": account,
                "collateralToken": collateral_token,
                "debtToken": debt_token
            }
        }
    
    def _get_chain_id(self, network: str) -> int:
        """Get chain ID for network"""
        chain_ids = {
            "ethereum": 1,
            "polygon": 137,
            "arbitrum": 42161
        }
        return chain_ids.get(network, 1)
    
    def export_for_transaction_builder(
        self,
        strategy: Dict[str, Any],
        filename: Optional[str] = None
    ) -> str:
        """
        Export strategy as JSON for Avocado transaction builder
        
        Args:
            strategy: Strategy to export
            filename: Optional filename to save to
            
        Returns:
            JSON string of the transaction batch
        """
        transaction_batch = self.strategy_to_avocado_transactions(strategy)
        json_output = json.dumps(transaction_batch, indent=2)
        
        if filename:
            with open(filename, 'w') as f:
                f.write(json_output)
            print(f"Transaction batch saved to {filename}")
        
        return json_output
    
    def create_simulation_data(
        self,
        strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create simulation data for testing before execution
        
        Args:
            strategy: Strategy to simulate
            
        Returns:
            Simulation parameters
        """
        return {
            "network": self.network,
            "wallet": self.wallet_address,
            "strategy": strategy,
            "estimated_gas": self._estimate_total_gas(strategy),
            "warnings": self._check_strategy_risks(strategy)
        }
    
    def _estimate_total_gas(self, strategy: Dict[str, Any]) -> int:
        """Estimate total gas for strategy execution"""
        # Rough estimates per action type
        gas_estimates = {
            "flash_loan": 150000,
            "swap": 100000,
            "liquidate": 200000,
            "repay_flash_loan": 50000
        }
        
        total_gas = 0
        for step in strategy.get("steps", []):
            action = step.get("action")
            total_gas += gas_estimates.get(action, 100000)
        
        return total_gas
    
    def _check_strategy_risks(self, strategy: Dict[str, Any]) -> List[str]:
        """Check for potential risks in strategy"""
        warnings = []
        
        # Check for high slippage
        slippage = strategy.get("slippage_tolerance", 0)
        if slippage > 1.0:
            warnings.append(f"High slippage tolerance: {slippage}%")
        
        # Check for complex multi-step strategies
        steps = strategy.get("steps", [])
        if len(steps) > 5:
            warnings.append(f"Complex strategy with {len(steps)} steps - higher gas costs")
        
        # Check deadline
        deadline = strategy.get("deadline", 0)
        if deadline < 60:
            warnings.append(f"Short deadline: {deadline} seconds")
        
        return warnings
