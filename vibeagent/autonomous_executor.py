"""
Autonomous Executor for VibeAgent
Handles real-time arbitrage scanning and autonomous transaction execution
with safety features and profit distribution
"""
import os
import time
from typing import Dict, List, Optional, Any
from decimal import Decimal
from datetime import datetime
from web3 import Web3
from dotenv import load_dotenv
from .agent import VibeAgent
from .wallet_connector import WalletConnector
from .contract_abis import CONTRACT_ADDRESSES, ERC20_ABI

load_dotenv()


class AutonomousExecutor:
    """
    Executes arbitrage transactions autonomously with safety checks
    """
    
    def __init__(
        self,
        agent: VibeAgent,
        wallet_connector: WalletConnector,
        min_profit_usd: float = None,
        max_gas_price_gwei: float = None
    ):
        """
        Initialize autonomous executor
        
        Args:
            agent: VibeAgent instance for strategy generation
            wallet_connector: WalletConnector instance for wallet interactions
            min_profit_usd: Minimum profit threshold in USD (from env if None)
            max_gas_price_gwei: Maximum gas price in Gwei (from env if None)
        """
        self.agent = agent
        self.wallet = wallet_connector
        self.web3 = wallet_connector.web3
        
        # Safety parameters
        self.min_profit_usd = min_profit_usd or float(os.getenv("MIN_PROFIT_USD", "50"))
        self.max_gas_price_gwei = max_gas_price_gwei or float(os.getenv("MAX_GAS_PRICE_GWEI", "100"))
        
        # Execution state
        self.is_scanning = False
        self.executed_opportunities = []
        self.failed_opportunities = []
        
        print(f"Autonomous Executor initialized")
        print(f"  Min Profit: ${self.min_profit_usd}")
        print(f"  Max Gas Price: {self.max_gas_price_gwei} Gwei")
    
    def validate_safety_checks(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive safety checks before execution
        
        Args:
            opportunity: Opportunity dictionary to validate
            
        Returns:
            Validation result with pass/fail and reasons
        """
        checks = {
            "passed": True,
            "checks": [],
            "warnings": [],
            "errors": []
        }
        
        # Check 1: Minimum profit threshold
        profit = opportunity.get("estimated_profit_usd", 0)
        if profit < self.min_profit_usd:
            checks["passed"] = False
            checks["errors"].append(
                f"Profit ${profit:.2f} below minimum ${self.min_profit_usd}"
            )
        else:
            checks["checks"].append(f"✓ Profit ${profit:.2f} exceeds minimum")
        
        # Check 2: Wallet connection
        if not self.wallet.connected:
            checks["passed"] = False
            checks["errors"].append("Wallet not connected")
        else:
            checks["checks"].append("✓ Wallet connected")
        
        # Check 3: Gas balance
        gas_estimate = opportunity.get("gas_estimate", 500000)
        gas_check = self.wallet.check_gas_balance(gas_estimate)
        
        if not gas_check.get("sufficient", False):
            checks["passed"] = False
            checks["errors"].append(
                f"Insufficient gas balance: {gas_check.get('warning', 'Unknown error')}"
            )
        else:
            checks["checks"].append(
                f"✓ Sufficient gas balance ({gas_check['current_balance']:.4f} {gas_check['native_token']})"
            )
        
        # Check 4: Gas price limit
        if not gas_check.get("gas_price_acceptable", True):
            checks["passed"] = False
            checks["errors"].append(
                f"Gas price {gas_check.get('current_gas_price_gwei', 0):.2f} Gwei exceeds maximum {self.max_gas_price_gwei} Gwei"
            )
        else:
            checks["checks"].append(
                f"✓ Gas price acceptable ({gas_check.get('current_gas_price_gwei', 0):.2f} Gwei)"
            )
        
        # Check 5: Network validation
        network_match = self.wallet.validate_network(self.agent.network)
        if not network_match:
            checks["passed"] = False
            checks["errors"].append(
                f"Network mismatch: wallet on {self.wallet.network}, agent on {self.agent.network}"
            )
        else:
            checks["checks"].append(f"✓ Network validated ({self.wallet.network})")
        
        # Check 6: Opportunity profitability
        if not opportunity.get("profitable", False):
            checks["passed"] = False
            checks["errors"].append("Opportunity marked as not profitable")
        else:
            checks["checks"].append("✓ Opportunity marked as profitable")
        
        # Warnings (don't fail but inform)
        slippage = opportunity.get("strategy", {}).get("slippage_tolerance", 0)
        if slippage > 1.0:
            checks["warnings"].append(f"High slippage tolerance: {slippage}%")
        
        return checks
    
    def scan_and_execute_arbitrage(
        self,
        token_pairs: List[tuple],
        dexes: List[str],
        continuous: bool = False,
        scan_interval: int = 60
    ) -> List[Dict[str, Any]]:
        """
        Scan for arbitrage opportunities and execute profitable ones
        
        Args:
            token_pairs: List of token pair tuples to scan
            dexes: List of DEXes to check
            continuous: If True, scan continuously
            scan_interval: Seconds between scans (for continuous mode)
            
        Returns:
            List of execution results
        """
        results = []
        self.is_scanning = True
        
        print(f"\n{'='*60}")
        print(f"Starting arbitrage scan...")
        print(f"Token pairs: {len(token_pairs)}")
        print(f"DEXes: {', '.join(dexes)}")
        print(f"Continuous: {continuous}")
        print(f"{'='*60}\n")
        
        try:
            iteration = 0
            while self.is_scanning:
                iteration += 1
                print(f"\n--- Scan iteration {iteration} at {datetime.now().strftime('%H:%M:%S')} ---")
                
                for token_pair in token_pairs:
                    try:
                        # Analyze opportunity
                        print(f"\nScanning {token_pair[0][:10]}.../{token_pair[1][:10]}...")
                        opportunity = self.agent.analyze_arbitrage_opportunity(
                            token_pair=token_pair,
                            dexes=dexes
                        )
                        
                        # Generate strategy
                        opportunity = self.agent.generate_strategy_with_ai(opportunity)
                        
                        # Validate safety checks
                        validation = self.validate_safety_checks(opportunity)
                        
                        if validation["passed"]:
                            print("\n✓ All safety checks passed! Executing...")
                            
                            # Execute the opportunity
                            execution_result = self.execute_arbitrage(opportunity)
                            results.append(execution_result)
                            
                            if execution_result["success"]:
                                print(f"✓ Execution successful!")
                                self.executed_opportunities.append({
                                    "opportunity": opportunity,
                                    "result": execution_result,
                                    "timestamp": datetime.now().isoformat()
                                })
                            else:
                                print(f"✗ Execution failed: {execution_result.get('error')}")
                                self.failed_opportunities.append({
                                    "opportunity": opportunity,
                                    "result": execution_result,
                                    "timestamp": datetime.now().isoformat()
                                })
                        else:
                            print(f"\n✗ Safety checks failed:")
                            for error in validation["errors"]:
                                print(f"  - {error}")
                            
                            for warning in validation["warnings"]:
                                print(f"  ⚠ {warning}")
                    
                    except Exception as e:
                        print(f"Error scanning token pair {token_pair}: {e}")
                        continue
                
                # Break if not continuous
                if not continuous:
                    break
                
                # Wait before next scan
                print(f"\nWaiting {scan_interval} seconds before next scan...")
                time.sleep(scan_interval)
        
        except KeyboardInterrupt:
            print("\n\nScan interrupted by user")
        finally:
            self.is_scanning = False
            print(f"\n{'='*60}")
            print(f"Scan completed")
            print(f"Successful executions: {len(self.executed_opportunities)}")
            print(f"Failed executions: {len(self.failed_opportunities)}")
            print(f"{'='*60}\n")
        
        return results
    
    def execute_arbitrage(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an arbitrage opportunity
        
        Args:
            opportunity: Opportunity with strategy to execute
            
        Returns:
            Execution result
        """
        print(f"\nExecuting arbitrage opportunity...")
        
        try:
            strategy = opportunity.get("strategy")
            if not strategy:
                return {
                    "success": False,
                    "error": "No strategy found in opportunity"
                }
            
            # Get strategy steps
            steps = strategy.get("steps", [])
            if not steps:
                return {
                    "success": False,
                    "error": "No steps found in strategy"
                }
            
            # For arbitrage, we need to execute the flash loan with all swaps
            # This is a simplified version - in production, you'd need a custom contract
            # that implements the full flash loan callback logic
            
            # Create transaction for the arbitrage contract call
            # Note: This would require a deployed arbitrage contract
            # For now, we'll create a simulated execution flow
            
            print("Creating arbitrage transaction...")
            
            # Get token addresses
            token_a, token_b = opportunity["token_pair"]
            
            # Build transaction data
            # In production, this would call your arbitrage contract
            transaction_data = self._build_arbitrage_transaction(opportunity)
            
            if transaction_data.get("simulated", True):
                # For demo/testing, simulate the execution
                return self._simulate_execution(opportunity)
            
            # Create transaction request
            tx_request = self.wallet.create_transaction_request(
                to=transaction_data["to"],
                data=transaction_data["data"],
                value=transaction_data.get("value", 0),
                gas_limit=strategy.get("estimated_gas")
            )
            
            if not tx_request["success"]:
                return {
                    "success": False,
                    "error": f"Failed to create transaction: {tx_request.get('error')}"
                }
            
            print(f"Transaction request created: {tx_request['request_id']}")
            print("Note: In browser, user needs to sign via WalletConnect")
            
            return {
                "success": True,
                "request_id": tx_request["request_id"],
                "transaction": tx_request["transaction"],
                "status": "pending_signature",
                "message": "Transaction created, awaiting user signature via WalletConnect"
            }
            
        except Exception as e:
            print(f"Error executing arbitrage: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _build_arbitrage_transaction(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build transaction data for arbitrage execution
        
        Args:
            opportunity: Opportunity details
            
        Returns:
            Transaction data dictionary
        """
        # In a real implementation, this would build the transaction to call
        # your deployed arbitrage contract with the appropriate parameters
        
        # For now, return a simulated flag since we don't have a deployed contract
        return {
            "simulated": True,
            "reason": "Arbitrage contract not deployed. Use simulation mode."
        }
    
    def _simulate_execution(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate execution for testing/demonstration
        
        Args:
            opportunity: Opportunity to simulate
            
        Returns:
            Simulation result
        """
        print("\n--- SIMULATION MODE ---")
        print("Simulating transaction execution...")
        
        strategy = opportunity.get("strategy", {})
        profit = opportunity.get("estimated_profit_usd", 0)
        
        # Simulate transaction
        time.sleep(1)  # Simulate network delay
        
        # Generate mock transaction hash
        mock_tx_hash = f"0x{'a' * 64}"
        
        print(f"✓ Transaction simulated successfully")
        print(f"  Mock TX Hash: {mock_tx_hash}")
        print(f"  Estimated Profit: ${profit:.2f}")
        print(f"  Profit would be sent to: {self.wallet.wallet_address}")
        
        return {
            "success": True,
            "simulated": True,
            "tx_hash": mock_tx_hash,
            "profit_usd": profit,
            "recipient": self.wallet.wallet_address,
            "status": "simulated",
            "message": "Execution simulated successfully. Deploy arbitrage contract for real execution."
        }
    
    def distribute_profit(
        self,
        profit_token: str,
        profit_amount: int,
        recipient: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Distribute profit back to the connected wallet
        
        Args:
            profit_token: Token address of the profit
            profit_amount: Amount of profit in token's smallest unit
            recipient: Recipient address (uses connected wallet if None)
            
        Returns:
            Distribution result
        """
        try:
            if not self.wallet.connected:
                return {
                    "success": False,
                    "error": "Wallet not connected"
                }
            
            recipient = recipient or self.wallet.wallet_address
            recipient = Web3.to_checksum_address(recipient)
            
            print(f"\nDistributing profit to {recipient}...")
            
            # Create ERC20 transfer transaction
            token_contract = self.web3.eth.contract(
                address=Web3.to_checksum_address(profit_token),
                abi=ERC20_ABI
            )
            
            # Build transfer transaction
            transfer_data = token_contract.functions.transfer(
                recipient,
                profit_amount
            )._encode_transaction_data()
            
            # Create transaction request
            tx_request = self.wallet.create_transaction_request(
                to=profit_token,
                data=transfer_data,
                value=0
            )
            
            if not tx_request["success"]:
                return {
                    "success": False,
                    "error": f"Failed to create transfer: {tx_request.get('error')}"
                }
            
            print(f"✓ Profit distribution transaction created")
            print(f"  Request ID: {tx_request['request_id']}")
            
            return {
                "success": True,
                "request_id": tx_request["request_id"],
                "transaction": tx_request["transaction"],
                "recipient": recipient,
                "status": "pending_signature"
            }
            
        except Exception as e:
            print(f"Error distributing profit: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def stop_scanning(self):
        """Stop continuous scanning"""
        print("\nStopping scan...")
        self.is_scanning = False
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """
        Get execution statistics
        
        Returns:
            Statistics dictionary
        """
        total_profit = sum(
            opp["opportunity"].get("estimated_profit_usd", 0)
            for opp in self.executed_opportunities
        )
        
        return {
            "successful_executions": len(self.executed_opportunities),
            "failed_executions": len(self.failed_opportunities),
            "total_profit_usd": total_profit,
            "is_scanning": self.is_scanning,
            "executed_opportunities": self.executed_opportunities,
            "failed_opportunities": self.failed_opportunities
        }
