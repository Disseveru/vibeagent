"""
Autonomous scanner for continuous monitoring of arbitrage opportunities
"""

import time
import threading
from typing import Dict, Any, List
from datetime import datetime
from collections import deque

from .agent import VibeAgent
from .config import AgentConfig
from .logger import VibeLogger
from .execution_engine import ExecutionEngine


class AutonomousScanner:
    """
    Continuously scans for arbitrage opportunities and executes them autonomously
    """

    def __init__(self, config: AgentConfig, logger: VibeLogger):
        self.config = config
        self.logger = logger

        # Initialize agents for each network
        self.agents = {}
        for network in config.networks:
            try:
                self.agents[network] = VibeAgent(network=network)
                self.logger.info(f"Initialized agent for {network}")
            except Exception as e:
                self.logger.error(f"Failed to initialize agent for {network}: {e}")

        # Initialize execution engines for each network
        self.execution_engines = {}
        for network in config.networks:
            self.execution_engines[network] = ExecutionEngine(config, logger, network)

        # Scanner state
        self.is_running = False
        self.scan_thread = None
        self.last_scan_time = None
        self.scan_count = 0

        # Discovered opportunities (use deque for O(1) append and automatic size limit)
        self.max_opportunities_history = 100
        self.opportunities = deque(maxlen=self.max_opportunities_history)

        # Scanner statistics
        self.stats = {
            "total_scans": 0,
            "opportunities_found": 0,
            "opportunities_executed": 0,
            "total_profit_usd": 0,
            "last_scan": None,
            "errors": 0,
        }

    def start(self):
        """Start the autonomous scanner"""
        if self.is_running:
            self.logger.warning("Scanner already running")
            return

        self.is_running = True
        self.scan_thread = threading.Thread(target=self._scan_loop, daemon=True)
        self.scan_thread.start()
        self.logger.info("Autonomous scanner started")

    def stop(self):
        """Stop the autonomous scanner"""
        if not self.is_running:
            return

        self.is_running = False
        if self.scan_thread:
            self.scan_thread.join(timeout=5)
        self.logger.info("Autonomous scanner stopped")

    def _scan_loop(self):
        """Main scanning loop"""
        self.logger.info(f"Starting scan loop with {self.config.scan_interval_seconds}s interval")

        while self.is_running:
            try:
                self._perform_scan()
                self.last_scan_time = datetime.now()
                self.scan_count += 1

                # Wait for next scan
                time.sleep(self.config.scan_interval_seconds)

            except Exception as e:
                self.logger.error(f"Error in scan loop: {e}")
                self.stats["errors"] += 1
                time.sleep(10)  # Wait before retrying

    def _perform_scan(self):
        """Perform a single scan cycle across all networks"""
        self.stats["total_scans"] += 1
        self.stats["last_scan"] = datetime.now().isoformat()

        for network in self.config.networks:
            try:
                self._scan_network(network)
            except Exception as e:
                self.logger.error(f"Error scanning {network}: {e}")
                self.stats["errors"] += 1

    def _scan_network(self, network: str):
        """Scan a specific network for opportunities"""
        agent = self.agents.get(network)
        if not agent:
            self.logger.warning(f"No agent available for {network}")
            return

        execution_engine = self.execution_engines.get(network)
        if not execution_engine:
            self.logger.warning(f"No execution engine for {network}")
            return

        self.logger.log_scan_start(network, len(self.config.monitored_token_pairs))

        # Scan all monitored token pairs
        for token_pair in self.config.monitored_token_pairs:
            try:
                # Skip blacklisted tokens
                if any(self.config.is_address_blacklisted(token) for token in token_pair):
                    continue

                # Analyze arbitrage opportunity
                opportunity = agent.analyze_arbitrage_opportunity(
                    token_pair=token_pair, dexes=self.config.enabled_dexes
                )

                # Check if profitable
                if opportunity.get("profitable", False):
                    self.logger.log_opportunity_found(opportunity)
                    self.stats["opportunities_found"] += 1

                    # Generate strategy (skip AI generation in autonomous mode for performance)
                    # AI generation is expensive (5-30s per call) and blocks the scan loop
                    # Only generate AI strategies on-demand via web interface
                    if not self.config.autonomous_mode:
                        opportunity = agent.generate_strategy_with_ai(opportunity)

                    opportunity["network"] = network
                    opportunity["discovered_at"] = datetime.now().isoformat()

                    # Store opportunity
                    self._store_opportunity(opportunity)

                    # Execute if autonomous mode is enabled
                    if self.config.autonomous_mode:
                        success = execution_engine.execute_opportunity(opportunity)
                        if success:
                            self.stats["opportunities_executed"] += 1
                            profit = opportunity.get("estimated_profit_usd", 0)
                            self.stats["total_profit_usd"] += profit

            except Exception as e:
                self.logger.error(f"Error scanning token pair {token_pair}: {e}")

    def _store_opportunity(self, opportunity: Dict[str, Any]):
        """Store discovered opportunity in history"""
        # deque with maxlen automatically removes oldest items
        self.opportunities.append(opportunity)

    def get_opportunities(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent opportunities"""
        # Convert deque to list and get last N items
        return list(self.opportunities)[-limit:]

    def get_status(self) -> Dict[str, Any]:
        """Get scanner status"""
        return {
            "is_running": self.is_running,
            "last_scan": self.last_scan_time.isoformat() if self.last_scan_time else None,
            "scan_count": self.scan_count,
            "networks": self.config.networks,
            "monitored_pairs": len(self.config.monitored_token_pairs),
            "enabled_dexes": self.config.enabled_dexes,
            "stats": self.stats,
            "config": {
                "autonomous_mode": self.config.autonomous_mode,
                "require_manual_approval": self.config.require_manual_approval,
                "scan_interval_seconds": self.config.scan_interval_seconds,
                "min_profit_usd": self.config.min_profit_usd,
                "max_gas_price_gwei": self.config.max_gas_price_gwei,
            },
        }

    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics from all networks"""
        combined_stats = {
            "total_executions": 0,
            "successful": 0,
            "failed": 0,
            "total_profit_usd": 0,
            "pending_approvals": 0,
            "by_network": {},
        }

        for network, engine in self.execution_engines.items():
            network_stats = engine.get_stats()
            combined_stats["by_network"][network] = network_stats
            combined_stats["total_executions"] += network_stats["total_executions"]
            combined_stats["successful"] += network_stats["successful"]
            combined_stats["failed"] += network_stats["failed"]
            combined_stats["total_profit_usd"] += network_stats["total_profit_usd"]
            combined_stats["pending_approvals"] += network_stats["pending_approvals"]

        return combined_stats

    def get_pending_approvals(self) -> List[Dict[str, Any]]:
        """Get all pending approvals across networks"""
        all_approvals = []
        for network, engine in self.execution_engines.items():
            approvals = engine.get_pending_approvals()
            for approval in approvals:
                approval["network"] = network
                all_approvals.append(approval)
        return all_approvals

    def approve_transaction(self, network: str, approval_id: str) -> bool:
        """Approve a pending transaction"""
        engine = self.execution_engines.get(network)
        if not engine:
            self.logger.error(f"No execution engine for {network}")
            return False
        return engine.approve_transaction(approval_id)

    def reject_transaction(self, network: str, approval_id: str) -> bool:
        """Reject a pending transaction"""
        engine = self.execution_engines.get(network)
        if not engine:
            return False
        return engine.reject_transaction(approval_id)

    def update_config(self, **kwargs):
        """Update scanner configuration"""
        self.config.update(**kwargs)
        self.logger.info(f"Configuration updated: {kwargs}")
