"""
Instadapp Avocado Multi-Sig Wallet Integration
Converts strategies into Avocado-compatible transaction batches
"""

from typing import Dict, List, Any, Optional
from web3 import Web3
import json
from datetime import datetime
from .contract_abis import (
    UNISWAP_V3_ROUTER_ABI,
    SUSHISWAP_ROUTER_ABI,
    AAVE_V3_POOL_ABI,
    CONTRACT_ADDRESSES,
)


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
                        {"name": "operation", "type": "uint8"},
                    ],
                },
                {"name": "id", "type": "uint256"},
            ],
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
        },
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
        self.web3 = Web3()  # Utility instance for encoding

    def strategy_to_avocado_transactions(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
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
            action = self._convert_step_to_action(step, strategy)
            if action:
                actions.append(action)

        # Build the transaction batch for Avocado
        return {
            "version": "1.0",
            "chainId": self._get_chain_id(self.network),
            "meta": {
                "name": f"{strategy.get('type', 'Strategy')} Execution",
                "description": f"Automated {strategy.get('type')} strategy",
                "createdBy": "VibeAgent",
            },
            "transactions": actions,
        }

    def _convert_step_to_action(self, step: Dict[str, Any], strategy: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Convert a strategy step into an Avocado action"""
        action_type = step.get("action")

        if action_type == "flash_loan":
            return self._build_flash_loan_action(step, strategy)
        elif action_type == "swap":
            return self._build_swap_action(step)
        elif action_type == "liquidate":
            return self._build_liquidation_action(step)
        elif action_type == "repay_flash_loan":
            # Usually handled in the flash loan callback
            return None

        return None

    def _build_flash_loan_action(self, step: Dict[str, Any], strategy: Dict[str, Any] = None) -> Dict[str, Any]:
        """Build flash loan action for Avocado"""
        protocol = step.get("protocol", "aave_v3")
        token = step.get("token")
        amount = step.get("amount", "auto")

        # Get protocol address
        pool_address = self.PROTOCOL_ADDRESSES[self.network].get(f"{protocol}_pool")

        # Encode flash loan call with strategy context for amount calculation
        encoded_data = self._encode_flash_loan_call(token, amount, strategy)

        return {
            "to": pool_address,
            "value": "0",
            "data": encoded_data,
            "operation": 0,  # CALL operation
            "description": f"Flash loan from {protocol}",
            "meta": {"protocol": protocol, "token": token, "amount": amount},
        }

    def _build_swap_action(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Build swap action for Avocado"""
        dex = step.get("dex", "uniswap_v3")
        from_token = step.get("from")
        to_token = step.get("to")
        amount = step.get("amount")  # Get amount from step if provided

        # Get DEX router address
        router_address = self.PROTOCOL_ADDRESSES[self.network].get(f"{dex}_router")

        # Encode swap call with amount if available
        encoded_data = self._encode_swap_call(dex, from_token, to_token, amount)

        return {
            "to": router_address,
            "value": "0",
            "data": encoded_data,
            "operation": 0,
            "description": f"Swap on {dex}",
            "meta": {"dex": dex, "fromToken": from_token, "toToken": to_token, "amount": amount},
        }

    def _build_liquidation_action(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Build liquidation action for Avocado"""
        protocol = step.get("protocol")
        account = step.get("account")
        collateral_token = step.get("collateral_token")
        debt_token = step.get("debt_token")

        # Get protocol address
        pool_address = self.PROTOCOL_ADDRESSES[self.network].get(f"{protocol}_pool")

        # Encode liquidation call
        encoded_data = self._encode_liquidation_call(collateral_token, debt_token, account)

        return {
            "to": pool_address,
            "value": "0",
            "data": encoded_data,
            "operation": 0,
            "description": f"Liquidate on {protocol}",
            "meta": {
                "protocol": protocol,
                "account": account,
                "collateralToken": collateral_token,
                "debtToken": debt_token,
            },
        }

    def _get_chain_id(self, network: str) -> int:
        """Get chain ID for network"""
        chain_ids = {"ethereum": 1, "polygon": 137, "arbitrum": 42161}
        return chain_ids.get(network, 1)

    def export_for_transaction_builder(
        self, strategy: Dict[str, Any], filename: Optional[str] = None
    ) -> str:
        """
        Export strategy as JSON for Avocado transaction builder

        Args:
            strategy: Strategy dict or opportunity dict with 'strategy' key
            filename: Optional filename to save to

        Returns:
            JSON string of the transaction batch
        """
        # Handle both opportunity and strategy objects
        if "strategy" in strategy and isinstance(strategy["strategy"], dict):
            # This is an opportunity object, extract the strategy
            actual_strategy = strategy["strategy"]
        else:
            # This is already a strategy object
            actual_strategy = strategy

        transaction_batch = self.strategy_to_avocado_transactions(actual_strategy)

        # Add metadata
        transaction_batch["meta"]["timestamp"] = datetime.now().isoformat()
        transaction_batch["meta"]["network"] = self.network
        transaction_batch["meta"]["wallet"] = self.wallet_address
        transaction_batch["meta"]["estimated_profit"] = actual_strategy.get(
            "estimated_profit_usd", 0
        )
        transaction_batch["meta"]["estimated_gas"] = actual_strategy.get("estimated_gas", 0)
        transaction_batch["meta"]["risk_level"] = self._assess_risk_level(actual_strategy)

        json_output = json.dumps(transaction_batch, indent=2)

        if filename:
            with open(filename, "w") as f:
                f.write(json_output)
            print(f"Transaction batch saved to {filename}")

        return json_output

    def _assess_risk_level(self, strategy: Dict[str, Any]) -> str:
        """Assess risk level of strategy"""
        warnings = self._check_strategy_risks(strategy)

        if len(warnings) == 0:
            return "low"
        elif len(warnings) <= 2:
            return "medium"
        else:
            return "high"

    def create_simulation_data(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create simulation data for testing before execution

        Args:
            strategy: Strategy to simulate

        Returns:
            Simulation parameters
        """
        total_gas = self._estimate_total_gas(strategy)
        warnings = self._check_strategy_risks(strategy)

        # Add 20% safety buffer to gas estimate
        gas_with_buffer = int(total_gas * 1.2)

        return {
            "network": self.network,
            "wallet": self.wallet_address,
            "strategy_type": strategy.get("type", "unknown"),
            "estimated_gas": total_gas,
            "gas_with_buffer": gas_with_buffer,
            "estimated_profit_usd": strategy.get("estimated_profit_usd", 0),
            "risk_level": self._assess_risk_level(strategy),
            "warnings": warnings,
            "steps_count": len(strategy.get("steps", [])),
            "simulation_recommendations": [
                "Test on fork/testnet first",
                "Monitor gas prices before execution",
                "Check for sufficient liquidity",
                "Be aware of MEV/frontrunning risks",
            ],
        }

    def _estimate_total_gas(self, strategy: Dict[str, Any]) -> int:
        """Estimate total gas for strategy execution"""
        # Rough estimates per action type
        gas_estimates = {
            "flash_loan": 150000,
            "swap": 100000,
            "liquidate": 200000,
            "repay_flash_loan": 50000,
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

    def _encode_flash_loan_call(self, token: str, amount: str, opportunity: Optional[Dict[str, Any]] = None) -> str:
        """
        Encode Aave V3 flash loan call

        Args:
            token: Token address to borrow
            amount: Amount to borrow (can be string like "10" or "auto")
            opportunity: Optional opportunity dict to calculate amount from

        Returns:
            Encoded calldata as hex string
        """
        try:
            token = Web3.to_checksum_address(token)

            # Calculate amount based on opportunity details or use provided amount
            if amount == "auto":
                # Try to calculate from opportunity details
                if opportunity:
                    # For liquidations, use max_liquidatable_usd
                    if opportunity.get("type") == "liquidation":
                        max_liquidatable_usd = opportunity.get("max_liquidatable_usd", 0)
                        # Convert USD to token amount (simplified - assumes 1:1 for stablecoins)
                        # In production, would query token price
                        amount_wei = int(max_liquidatable_usd * (10**18))
                    # For arbitrage, use a reasonable amount based on estimated profit
                    elif opportunity.get("type") == "arbitrage":
                        # Use 10x the estimated profit as loan amount
                        estimated_profit = opportunity.get("estimated_profit_usd", 0)
                        amount_wei = int(max(10 * estimated_profit, 1) * (10**18))
                    else:
                        amount_wei = 1 * (10**18)  # Default 1 token
                else:
                    amount_wei = 1 * (10**18)  # Default 1 token when no opportunity data
            elif not amount.isdigit():
                # If amount is not "auto" but also not a number, use default
                amount_wei = 1 * (10**18)
            else:
                amount_wei = int(float(amount) * (10**18))

            # Get pool address
            pool_address = CONTRACT_ADDRESSES[self.network]["aave_v3_pool"]

            # Create contract instance for encoding
            pool = self.web3.eth.contract(address=pool_address, abi=AAVE_V3_POOL_ABI)

            # Encode flashLoan function call
            # flashLoan(receiverAddress, assets[], amounts[], modes[],
            # onBehalfOf, params, referralCode)
            encoded = pool.functions.flashLoan(
                self.wallet_address,  # receiver
                [token],  # assets array
                [amount_wei],  # amounts array
                [0],  # modes (0 = no debt, flash loan only)
                self.wallet_address,  # onBehalfOf
                b"",  # params (empty bytes)
                0,  # referralCode
            )._encode_transaction_data()
            return encoded

        except Exception as e:
            print(f"Error encoding flash loan: {e}")
            return "0x"

    def _encode_swap_call(self, dex: str, from_token: str, to_token: str, amount: Optional[int] = None) -> str:
        """
        Encode DEX swap call

        Args:
            dex: DEX name (uniswap_v3, sushiswap)
            from_token: Input token address
            to_token: Output token address
            amount: Amount to swap in wei (if None, uses 1 token as placeholder)

        Returns:
            Encoded calldata as hex string
        """
        try:
            from_token = Web3.to_checksum_address(from_token)
            to_token = Web3.to_checksum_address(to_token)
            
            # Use provided amount or default to 1 token (10**18 wei)
            # In production, this should always be calculated from strategy details
            amount_in = amount if amount is not None else 10**18

            if dex == "uniswap_v3":
                # Get router address
                router_address = CONTRACT_ADDRESSES[self.network]["uniswap_v3_router"]

                # Encode Uniswap V3 exactInputSingle
                router = self.web3.eth.contract(address=router_address, abi=UNISWAP_V3_ROUTER_ABI)

                encoded = router.functions.exactInputSingle(
                    (
                        from_token,  # tokenIn
                        to_token,  # tokenOut
                        3000,  # fee (0.3%)
                        self.wallet_address,  # recipient
                        int(datetime.now().timestamp()) + 300,  # deadline (5 min)
                        amount_in,  # amountIn
                        0,  # amountOutMinimum (would calculate with slippage)
                        0,  # sqrtPriceLimitX96
                    )
                )._encode_transaction_data()
                return encoded

            elif dex == "sushiswap":
                # Get router address
                router_address = CONTRACT_ADDRESSES[self.network]["sushiswap_router"]

                # Encode SushiSwap swapExactTokensForTokens
                router = self.web3.eth.contract(address=router_address, abi=SUSHISWAP_ROUTER_ABI)

                encoded = router.functions.swapExactTokensForTokens(
                    amount_in,  # amountIn
                    0,  # amountOutMin (would calculate with slippage)
                    [from_token, to_token],  # path
                    self.wallet_address,  # to
                    int(datetime.now().timestamp()) + 300,  # deadline
                )._encode_transaction_data()
                return encoded

            else:
                print(f"Unknown DEX: {dex}")
                return "0x"

        except Exception as e:
            print(f"Error encoding swap: {e}")
            return "0x"

    def _encode_liquidation_call(self, collateral_token: str, debt_token: str, user: str) -> str:
        """
        Encode Aave V3 liquidation call

        Args:
            collateral_token: Collateral asset address
            debt_token: Debt asset address
            user: User address to liquidate

        Returns:
            Encoded calldata as hex string
        """
        try:
            collateral_token = Web3.to_checksum_address(collateral_token)
            debt_token = Web3.to_checksum_address(debt_token)
            user = Web3.to_checksum_address(user)

            # Get pool address
            pool_address = CONTRACT_ADDRESSES[self.network]["aave_v3_pool"]

            # Create contract instance for encoding
            pool = self.web3.eth.contract(address=pool_address, abi=AAVE_V3_POOL_ABI)

            # Encode liquidationCall
            # liquidationCall(collateralAsset, debtAsset, user, debtToCover, receiveAToken)
            encoded = pool.functions.liquidationCall(
                collateral_token,  # collateral asset
                debt_token,  # debt asset
                user,  # user to liquidate
                2**256 - 1,  # max uint256 (liquidate as much as possible)
                False,  # receive aToken (False = receive underlying)
            )._encode_transaction_data()
            return encoded

        except Exception as e:
            print(f"Error encoding liquidation: {e}")
            return "0x"
