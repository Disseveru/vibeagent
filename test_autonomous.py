"""
Tests for autonomous agent components
"""

import pytest
import os
from unittest.mock import patch
from vibeagent.config import AgentConfig
from vibeagent.logger import VibeLogger
from vibeagent.execution_engine import ExecutionEngine
from vibeagent.autonomous_scanner import AutonomousScanner


class TestConfig:
    """Test configuration management"""

    def test_config_initialization(self):
        """Test that config initializes with defaults"""
        config = AgentConfig()
        assert config.min_profit_usd >= 0
        assert config.max_gas_price_gwei > 0
        assert config.scan_interval_seconds > 0
        assert isinstance(config.networks, list)
        assert isinstance(config.enabled_dexes, list)

    def test_config_blacklist_check(self):
        """Test blacklist functionality"""
        config = AgentConfig()
        config.blacklisted_addresses = ["0xABC", "0xDEF"]

        assert config.is_address_blacklisted("0xABC")
        assert config.is_address_blacklisted("0xabc")  # Case insensitive
        assert not config.is_address_blacklisted("0x123")

    def test_config_blacklist_cache_refresh(self):
        """Blacklist set should refresh on reassignment"""
        config = AgentConfig()
        config.blacklisted_addresses = ["0xAAA"]
        assert config.is_address_blacklisted("0xaaa")

        # Reassign should rebuild the cached set
        config.blacklisted_addresses = ["0xBBB"]
        assert not config.is_address_blacklisted("0xaaa")
        assert config.is_address_blacklisted("0xbbb")

    def test_config_profit_check(self):
        """Test profit threshold checking"""
        config = AgentConfig()
        config.min_profit_usd = 50

        assert config.is_profitable(100)
        assert config.is_profitable(50)
        assert not config.is_profitable(49)

    def test_config_gas_check(self):
        """Test gas price checking"""
        config = AgentConfig()
        config.max_gas_price_gwei = 100

        assert config.is_gas_acceptable(50)
        assert config.is_gas_acceptable(100)
        assert not config.is_gas_acceptable(101)

    def test_config_to_dict(self):
        """Test config serialization"""
        config = AgentConfig()
        config_dict = config.to_dict()

        assert isinstance(config_dict, dict)
        assert "min_profit_usd" in config_dict
        assert "autonomous_mode" in config_dict
        assert "networks" in config_dict

    def test_config_update(self):
        """Test config update"""
        config = AgentConfig()
        original_profit = config.min_profit_usd

        config.update(min_profit_usd=100)
        assert config.min_profit_usd == 100
        assert config.min_profit_usd != original_profit


class TestLogger:
    """Test logging functionality"""

    def test_logger_initialization(self):
        """Test logger initializes correctly"""
        logger = VibeLogger(log_file="/tmp/test_vibeagent.log")
        assert logger.logger is not None
        assert logger.log_file == "/tmp/test_vibeagent.log"

    def test_logger_methods(self):
        """Test logging methods don't raise errors"""
        logger = VibeLogger(log_file="/tmp/test_vibeagent.log")

        # These should not raise exceptions
        logger.info("Test info message")
        logger.warning("Test warning message")
        logger.error("Test error message")
        logger.debug("Test debug message")

    def test_logger_scan_logging(self):
        """Test scan-specific logging"""
        logger = VibeLogger(log_file="/tmp/test_vibeagent.log")

        logger.log_scan_start("ethereum", 5)

        opportunity = {"type": "arbitrage", "estimated_profit_usd": 100}
        logger.log_opportunity_found(opportunity)
        logger.log_opportunity_rejected("Low profit", opportunity)

    def test_logger_transaction_logging(self):
        """Test transaction logging"""
        logger = VibeLogger(log_file="/tmp/test_vibeagent.log")

        opportunity = {"type": "arbitrage", "estimated_profit_usd": 100}

        logger.log_transaction_submitted("0x123", opportunity)
        logger.log_transaction_success("0x123", 100)
        logger.log_transaction_failure("0x123", "Test error")

    def test_logger_transaction_history(self):
        """Test transaction history retrieval"""
        logger = VibeLogger(log_file="/tmp/test_vibeagent.log")

        # Override transaction log file for testing
        logger.transaction_log_file = "/tmp/test_transactions.jsonl"

        # Log some transactions
        logger.log_transaction_submitted("0x123", {"type": "test"})
        logger.log_transaction_success("0x123", 100)

        # Retrieve history
        history = logger.get_transaction_history(limit=10)
        assert isinstance(history, list)


class TestExecutionEngine:
    """Test execution engine"""

    def test_execution_engine_initialization(self):
        """Test execution engine initializes"""
        config = AgentConfig()
        logger = VibeLogger(log_file="/tmp/test_vibeagent.log")

        # Don't set wallet address to avoid real initialization
        config.avocado_wallet_address = ""

        engine = ExecutionEngine(config, logger, "ethereum")
        assert engine.config == config
        assert engine.logger == logger
        assert engine.network == "ethereum"
        assert engine.avocado is None  # No wallet configured

    def test_execution_safety_checks(self):
        """Test safety check logic"""
        config = AgentConfig()
        config.min_profit_usd = 50
        config.max_gas_price_gwei = 100
        config.avocado_wallet_address = "0x1234567890123456789012345678901234567890"

        logger = VibeLogger(log_file="/tmp/test_vibeagent.log")

        # Mock RPC URL for testing
        os.environ["ETHEREUM_RPC_URL"] = "https://eth.llamarpc.com"

        engine = ExecutionEngine(config, logger, "ethereum")

        # Test profitable opportunity
        opportunity = {
            "type": "arbitrage",
            "estimated_profit_usd": 100,
            "gas_price_gwei": 50,
            "token_pair": (
                "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
                "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
            ),
        }
        can_execute, reason = engine.can_execute(opportunity)
        assert can_execute
        assert reason == "All safety checks passed"

        # Test low profit
        low_profit_opp = opportunity.copy()
        low_profit_opp["estimated_profit_usd"] = 30
        can_execute, reason = engine.can_execute(low_profit_opp)
        assert not can_execute
        assert "below minimum" in reason

        # Test high gas price
        high_gas_opp = opportunity.copy()
        high_gas_opp["gas_price_gwei"] = 150
        can_execute, reason = engine.can_execute(high_gas_opp)
        assert not can_execute
        assert "exceeds maximum" in reason

        # Test blacklisted token
        config.blacklisted_addresses = ["0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"]
        blacklist_opp = opportunity.copy()
        can_execute, reason = engine.can_execute(blacklist_opp)
        assert not can_execute
        assert "blacklisted" in reason

    def test_pending_approvals(self):
        """Test approval queue functionality"""
        config = AgentConfig()
        config.avocado_wallet_address = ""
        logger = VibeLogger(log_file="/tmp/test_vibeagent.log")

        engine = ExecutionEngine(config, logger, "ethereum")

        opportunity = {"type": "arbitrage", "estimated_profit_usd": 100}

        # Submit for approval
        approval_id = engine.submit_for_approval(opportunity)
        assert approval_id is not None
        assert approval_id in engine.pending_approvals

        # Get pending approvals
        pending = engine.get_pending_approvals()
        assert len(pending) == 1
        assert pending[0]["approval_id"] == approval_id

        # Reject
        success = engine.reject_transaction(approval_id)
        assert success
        assert engine.pending_approvals[approval_id]["status"] == "rejected"

    def test_execution_history(self):
        """Test execution history tracking"""
        config = AgentConfig()
        config.avocado_wallet_address = ""
        logger = VibeLogger(log_file="/tmp/test_vibeagent.log")

        engine = ExecutionEngine(config, logger, "ethereum")

        # Initially empty
        history = engine.get_execution_history()
        assert len(history) == 0

        # Stats should be zero
        stats = engine.get_stats()
        assert stats["total_executions"] == 0
        assert stats["successful"] == 0
        assert stats["failed"] == 0


class TestAutonomousScanner:
    """Test autonomous scanner"""

    def test_scanner_initialization(self):
        """Test scanner initializes"""
        config = AgentConfig()
        logger = VibeLogger(log_file="/tmp/test_vibeagent.log")

        # Mock RPC URLs
        os.environ["ETHEREUM_RPC_URL"] = "https://eth.llamarpc.com"
        os.environ["POLYGON_RPC_URL"] = "https://polygon-rpc.com"
        os.environ["ARBITRUM_RPC_URL"] = "https://arb1.arbitrum.io/rpc"

        scanner = AutonomousScanner(config, logger)

        assert scanner.config == config
        assert scanner.logger == logger
        assert not scanner.is_running
        assert scanner.scan_count == 0

    def test_scanner_status(self):
        """Test status reporting"""
        config = AgentConfig()
        logger = VibeLogger(log_file="/tmp/test_vibeagent.log")

        os.environ["ETHEREUM_RPC_URL"] = "https://eth.llamarpc.com"

        scanner = AutonomousScanner(config, logger)

        status = scanner.get_status()
        assert isinstance(status, dict)
        assert "is_running" in status
        assert "networks" in status
        assert "stats" in status
        assert status["is_running"] is False

    def test_scanner_opportunities(self):
        """Test opportunity storage"""
        config = AgentConfig()
        logger = VibeLogger(log_file="/tmp/test_vibeagent.log")

        os.environ["ETHEREUM_RPC_URL"] = "https://eth.llamarpc.com"

        scanner = AutonomousScanner(config, logger)

        # Initially empty
        opportunities = scanner.get_opportunities()
        assert len(opportunities) == 0

        # Store an opportunity
        opportunity = {
            "type": "arbitrage",
            "estimated_profit_usd": 100,
            "discovered_at": "2024-01-01T00:00:00",
        }
        scanner._store_opportunity(opportunity)

        # Should have one opportunity
        opportunities = scanner.get_opportunities()
        assert len(opportunities) == 1

    def test_scanner_stats(self):
        """Test statistics tracking"""
        config = AgentConfig()
        logger = VibeLogger(log_file="/tmp/test_vibeagent.log")

        os.environ["ETHEREUM_RPC_URL"] = "https://eth.llamarpc.com"

        scanner = AutonomousScanner(config, logger)

        stats = scanner.get_execution_stats()
        assert isinstance(stats, dict)
        assert "total_executions" in stats
        assert "successful" in stats
        assert "total_profit_usd" in stats

    def test_scanner_config_update(self):
        """Test configuration updates"""
        config = AgentConfig()
        logger = VibeLogger(log_file="/tmp/test_vibeagent.log")

        os.environ["ETHEREUM_RPC_URL"] = "https://eth.llamarpc.com"

        scanner = AutonomousScanner(config, logger)

        # Update config
        scanner.update_config(min_profit_usd=100, scan_interval_seconds=30)

        # Check it was applied
        assert scanner.config.min_profit_usd == 100
        assert scanner.config.scan_interval_seconds == 30


class TestVibeAgent:
    """Test VibeAgent price fetching functionality"""

    # Test RPC endpoint
    TEST_RPC_URL = "https://eth.llamarpc.com"

    # Reasonable bounds for ETH price (using wide range to handle volatility)
    MIN_REASONABLE_ETH_PRICE = 100
    MAX_REASONABLE_ETH_PRICE = 10000

    def test_eth_price_fetching(self):
        """Test that ETH price can be fetched from DEX"""
        # Use environment variable patch to avoid test pollution
        with patch.dict(os.environ, {"ETHEREUM_RPC_URL": self.TEST_RPC_URL}):
            # Import after env is set
            from vibeagent.agent import VibeAgent

            agent = VibeAgent(network="ethereum")

            # Test ETH price fetching
            eth_price = agent._get_eth_price_usd()

            # Price should be reasonable (between $100 and $10000)
            # Using wide range to avoid test failures due to market volatility
            assert isinstance(eth_price, float)
            assert self.MIN_REASONABLE_ETH_PRICE <= eth_price <= self.MAX_REASONABLE_ETH_PRICE

    def test_eth_price_fallback(self):
        """Test that ETH price falls back to 2000 when DEX queries fail"""
        with patch.dict(os.environ, {"ETHEREUM_RPC_URL": self.TEST_RPC_URL}):
            from vibeagent.agent import VibeAgent

            agent = VibeAgent(network="ethereum")

            # Mock _get_dex_price to return None (simulating failure)
            with patch.object(agent, "_get_dex_price", return_value=None):
                eth_price = agent._get_eth_price_usd()

            # Should fallback to 2000
            assert eth_price == 2000.0

    def test_gas_cost_estimation(self):
        """Test that gas cost estimation uses real ETH price"""
        with patch.dict(os.environ, {"ETHEREUM_RPC_URL": self.TEST_RPC_URL}):
            from vibeagent.agent import VibeAgent

            agent = VibeAgent(network="ethereum")

            # Mock _get_eth_price_usd to return a known value
            with patch.object(agent, "_get_eth_price_usd", return_value=2000.0):
                # Call the gas cost estimation which should use our mocked ETH price
                gas_cost = agent._estimate_gas_cost(gas_units=500000)

            # Should return an integer
            assert isinstance(gas_cost, int)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
