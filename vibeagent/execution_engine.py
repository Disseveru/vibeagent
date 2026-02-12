"""
Execution engine for autonomous transaction execution
"""
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import time
from web3 import Web3

from .config import AgentConfig
from .logger import VibeLogger
from .avocado_integration import AvocadoIntegration


class ExecutionEngine:
    """
    Handles execution of profitable opportunities
    Integrates with Avocado wallet for transaction submission
    """
    
    def __init__(self, config: AgentConfig, logger: VibeLogger, network: str = "ethereum"):
        self.config = config
        self.logger = logger
        self.network = network
        
        # Initialize Avocado integration
        if config.avocado_wallet_address:
            self.avocado = AvocadoIntegration(
                wallet_address=config.avocado_wallet_address,
                network=network
            )
        else:
            self.avocado = None
            self.logger.warning("No Avocado wallet configured - execution disabled")
        
        # Pending approvals for manual mode
        self.pending_approvals = {}
        
        # Execution history
        self.execution_history = []
        
    def can_execute(self, opportunity: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Check if opportunity passes all safety checks
        
        Returns:
            Tuple of (can_execute: bool, reason: str)
        """
        # Check if profitable enough
        profit = opportunity.get("estimated_profit_usd", 0)
        if not self.config.is_profitable(profit):
            reason = f"Profit ${profit:.2f} below minimum ${self.config.min_profit_usd}"
            self.logger.log_safety_check_failed("min_profit", {"profit": profit})
            return False, reason
        
        # Check gas price
        gas_price_gwei = opportunity.get("gas_price_gwei")
        if gas_price_gwei and not self.config.is_gas_acceptable(gas_price_gwei):
            reason = f"Gas price {gas_price_gwei} gwei exceeds maximum {self.config.max_gas_price_gwei}"
            self.logger.log_safety_check_failed("max_gas", {"gas_price": gas_price_gwei})
            return False, reason
        
        # Check for blacklisted addresses
        token_pair = opportunity.get("token_pair", ())
        for token in token_pair:
            if self.config.is_address_blacklisted(token):
                reason = f"Token {token} is blacklisted"
                self.logger.log_safety_check_failed("blacklist", {"address": token})
                return False, reason
        
        # Check if Avocado wallet is configured
        if not self.avocado:
            reason = "Avocado wallet not configured"
            return False, reason
        
        return True, "All safety checks passed"
    
    def prepare_transaction(self, opportunity: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Prepare transaction from opportunity strategy
        
        Returns:
            Transaction batch dict ready for Avocado wallet
        """
        if not opportunity.get("strategy"):
            self.logger.error("Opportunity has no strategy")
            return None
        
        try:
            # Convert strategy to Avocado transaction format
            tx_batch = self.avocado.strategy_to_avocado_transactions(opportunity["strategy"])
            
            # Add metadata
            tx_batch["metadata"] = {
                "opportunity_type": opportunity.get("type"),
                "estimated_profit_usd": opportunity.get("estimated_profit_usd"),
                "created_at": datetime.now().isoformat(),
                "network": self.network
            }
            
            return tx_batch
        except Exception as e:
            self.logger.error(f"Failed to prepare transaction: {e}")
            return None
    
    def submit_for_approval(self, opportunity: Dict[str, Any]) -> str:
        """
        Submit opportunity for manual approval
        
        Returns:
            Approval ID
        """
        approval_id = f"approval_{int(time.time())}_{len(self.pending_approvals)}"
        
        self.pending_approvals[approval_id] = {
            "opportunity": opportunity,
            "submitted_at": datetime.now().isoformat(),
            "status": "pending"
        }
        
        self.logger.info(f"Opportunity submitted for approval: {approval_id}")
        return approval_id
    
    def approve_transaction(self, approval_id: str) -> bool:
        """
        Approve a pending transaction for execution
        
        Returns:
            True if approved and queued for execution
        """
        if approval_id not in self.pending_approvals:
            self.logger.error(f"Approval ID not found: {approval_id}")
            return False
        
        approval = self.pending_approvals[approval_id]
        approval["status"] = "approved"
        approval["approved_at"] = datetime.now().isoformat()
        
        self.logger.info(f"Transaction approved: {approval_id}")
        
        # Execute immediately
        return self._execute_opportunity(approval["opportunity"])
    
    def reject_transaction(self, approval_id: str) -> bool:
        """
        Reject a pending transaction
        
        Returns:
            True if rejected successfully
        """
        if approval_id not in self.pending_approvals:
            return False
        
        approval = self.pending_approvals[approval_id]
        approval["status"] = "rejected"
        approval["rejected_at"] = datetime.now().isoformat()
        
        self.logger.info(f"Transaction rejected: {approval_id}")
        return True
    
    def execute_opportunity(self, opportunity: Dict[str, Any]) -> bool:
        """
        Execute opportunity (with or without approval based on config)
        
        Returns:
            True if executed or queued for approval
        """
        # Run safety checks
        can_execute, reason = self.can_execute(opportunity)
        if not can_execute:
            self.logger.log_opportunity_rejected(reason, opportunity)
            return False
        
        # Check if manual approval is required
        if self.config.require_manual_approval:
            approval_id = self.submit_for_approval(opportunity)
            self.logger.info(f"Opportunity requires manual approval: {approval_id}")
            return True  # Queued for approval
        
        # Execute immediately in autonomous mode
        return self._execute_opportunity(opportunity)
    
    def _execute_opportunity(self, opportunity: Dict[str, Any]) -> bool:
        """
        Internal method to execute opportunity
        
        Returns:
            True if execution succeeded
        """
        try:
            # Prepare transaction
            tx_batch = self.prepare_transaction(opportunity)
            if not tx_batch:
                return False
            
            # In a real implementation, this would:
            # 1. Sign the transaction batch with the Avocado wallet
            # 2. Submit to the network
            # 3. Monitor for confirmation
            # 4. Handle success/failure
            
            # For now, we'll simulate success and log the transaction
            tx_hash = f"0x{int(time.time()):x}"  # Simulated tx hash
            
            self.logger.log_transaction_submitted(tx_hash, opportunity)
            
            # Record in history
            execution_record = {
                "tx_hash": tx_hash,
                "opportunity": opportunity,
                "tx_batch": tx_batch,
                "executed_at": datetime.now().isoformat(),
                "status": "submitted",
                "network": self.network
            }
            self.execution_history.append(execution_record)
            
            # Simulate success (in reality, wait for confirmation)
            profit = opportunity.get("estimated_profit_usd", 0)
            self.logger.log_transaction_success(tx_hash, profit)
            execution_record["status"] = "success"
            execution_record["actual_profit_usd"] = profit
            
            return True
            
        except Exception as e:
            self.logger.log_transaction_failure(None, str(e))
            return False
    
    def get_pending_approvals(self) -> list:
        """Get list of pending approvals"""
        return [
            {
                "approval_id": approval_id,
                **approval_data
            }
            for approval_id, approval_data in self.pending_approvals.items()
            if approval_data["status"] == "pending"
        ]
    
    def get_execution_history(self, limit: int = 50) -> list:
        """Get execution history"""
        return self.execution_history[-limit:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        total_executions = len(self.execution_history)
        successful = sum(1 for ex in self.execution_history if ex.get("status") == "success")
        failed = total_executions - successful
        
        total_profit = sum(
            ex.get("actual_profit_usd", 0)
            for ex in self.execution_history
            if ex.get("status") == "success"
        )
        
        return {
            "total_executions": total_executions,
            "successful": successful,
            "failed": failed,
            "total_profit_usd": total_profit,
            "pending_approvals": len(self.get_pending_approvals())
        }
