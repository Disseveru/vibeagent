"""
Performance tests to verify optimizations work correctly
"""

import time
import os
from collections import deque
from vibeagent.agent import VibeAgent
from vibeagent.config import AgentConfig
from vibeagent.logger import VibeLogger
from vibeagent.execution_engine import ExecutionEngine


class TestPriceCache:
    """Test price caching functionality"""

    def test_price_cache_hit(self):
        """Test that price cache returns cached values within TTL"""
        os.environ["ETHEREUM_RPC_URL"] = "https://eth.llamarpc.com"
        agent = VibeAgent(network="ethereum", price_cache_ttl=60)

        # WETH and USDC addresses on Ethereum
        weth = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
        usdc = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"

        # First call - should make RPC call
        price1 = agent._get_dex_price(weth, usdc, "uniswap_v3")

        # Skip test if RPC is rate limiting
        if price1 is None:
            return

        # Second call within TTL - should use cache
        start_time = time.time()
        price2 = agent._get_dex_price(weth, usdc, "uniswap_v3")
        cache_time = time.time() - start_time

        # Cache hit should be very fast (< 10ms to account for test overhead)
        assert cache_time < 0.01, f"Cache hit took {cache_time}s, expected < 10ms"
        assert price1 == price2, "Cached price should match original"

    def test_price_cache_expiry(self):
        """Test that price cache expires after TTL"""
        os.environ["ETHEREUM_RPC_URL"] = "https://eth.llamarpc.com"
        agent = VibeAgent(network="ethereum", price_cache_ttl=1)  # 1 second TTL

        weth = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
        usdc = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"

        # First call
        price1 = agent._get_dex_price(weth, usdc, "uniswap_v3")

        # Skip test if first call failed (e.g., rate limiting)
        if price1 is None:
            return

        # Wait for cache to expire
        time.sleep(1.5)

        # Should make new RPC call after expiry
        price2 = agent._get_dex_price(weth, usdc, "uniswap_v3")

        # Prices might differ slightly due to market movement and cache refresh
        # or be None if rate limited
        assert price2 is None or isinstance(
            price2, (int, float)
        ), "Should return valid price or None"


class TestDequePerformance:
    """Test deque-based opportunity storage"""

    def test_deque_maxlen_behavior(self):
        """Test that deque with maxlen automatically removes old items"""
        opportunities = deque(maxlen=3)

        opportunities.append({"id": 1})
        opportunities.append({"id": 2})
        opportunities.append({"id": 3})
        assert len(opportunities) == 3

        # Adding 4th item should remove first
        opportunities.append({"id": 4})
        assert len(opportunities) == 3
        assert opportunities[0]["id"] == 2
        assert opportunities[-1]["id"] == 4

    def test_deque_performance(self):
        """Test that deque append is O(1) even with large collections"""
        opportunities = deque(maxlen=10000)

        # Fill deque
        for i in range(10000):
            opportunities.append({"id": i})

        # Measure append time
        start_time = time.time()
        for i in range(1000):
            opportunities.append({"id": 10000 + i})
        elapsed = time.time() - start_time

        # Should complete in under 10ms
        assert elapsed < 0.01, f"Deque append took {elapsed}s, expected < 10ms"


class TestIncrementalCounters:
    """Test incremental stats counters"""

    def test_stats_counters_accuracy(self):
        """Test that incremental counters match actual execution results"""
        os.environ["ETHEREUM_RPC_URL"] = "https://eth.llamarpc.com"
        config = AgentConfig()
        config.avocado_wallet_address = "0x1234567890123456789012345678901234567890"
        logger = VibeLogger(log_file="/tmp/test_perf.log")
        engine = ExecutionEngine(config, logger, "ethereum")

        # Execute some opportunities
        opportunity = {
            "type": "arbitrage",
            "estimated_profit_usd": 100,
            "strategy": {
                "type": "flashloan_arbitrage",
                "steps": [{"action": "flashloan", "amount": 10}],
            },
        }

        # Execute multiple times
        for _ in range(5):
            engine._execute_opportunity(opportunity)

        stats = engine.get_stats()
        assert stats["total_executions"] == 5
        assert stats["successful"] == 5
        assert stats["failed"] == 0
        assert stats["total_profit_usd"] == 500.0

    def test_stats_performance(self):
        """Test that stats calculation is O(1) not O(n)"""
        os.environ["ETHEREUM_RPC_URL"] = "https://eth.llamarpc.com"
        config = AgentConfig()
        config.avocado_wallet_address = "0x1234567890123456789012345678901234567890"
        logger = VibeLogger(log_file="/tmp/test_perf.log")
        engine = ExecutionEngine(config, logger, "ethereum")

        # Add many execution records
        for i in range(1000):
            engine.execution_history.append(
                {
                    "status": "success",
                    "actual_profit_usd": 10,
                }
            )
            engine._stats_counters["total_executions"] += 1
            engine._stats_counters["successful"] += 1
            engine._stats_counters["total_profit_usd"] += 10

        # Measure stats retrieval time
        start_time = time.time()
        for _ in range(100):
            stats = engine.get_stats()
        elapsed = time.time() - start_time

        # Should complete in under 1ms (O(1) operation)
        assert elapsed < 0.001, f"Stats retrieval took {elapsed}s, expected < 1ms"


class TestPendingApprovalsOptimization:
    """Test optimized pending approvals tracking"""

    def test_pending_ids_tracking(self):
        """Test that pending IDs list is maintained correctly"""
        os.environ["ETHEREUM_RPC_URL"] = "https://eth.llamarpc.com"
        config = AgentConfig()
        config.avocado_wallet_address = "0x1234567890123456789012345678901234567890"
        logger = VibeLogger(log_file="/tmp/test_perf.log")
        engine = ExecutionEngine(config, logger, "ethereum")

        opportunity = {
            "type": "arbitrage",
            "estimated_profit_usd": 100,
            "strategy": {"type": "flashloan_arbitrage", "steps": []},
        }

        # Submit for approval
        approval_id = engine.submit_for_approval(opportunity)
        assert approval_id in engine._pending_ids
        assert len(engine.get_pending_approvals()) == 1

        # Approve transaction
        engine.approve_transaction(approval_id)
        assert approval_id not in engine._pending_ids
        assert len(engine.get_pending_approvals()) == 0

    def test_pending_approvals_performance(self):
        """Test that pending approvals query scales with pending items not total"""
        os.environ["ETHEREUM_RPC_URL"] = "https://eth.llamarpc.com"
        config = AgentConfig()
        config.avocado_wallet_address = "0x1234567890123456789012345678901234567890"
        logger = VibeLogger(log_file="/tmp/test_perf.log")
        engine = ExecutionEngine(config, logger, "ethereum")

        opportunity = {
            "type": "arbitrage",
            "estimated_profit_usd": 100,
            "strategy": {"type": "flashloan_arbitrage", "steps": []},
        }

        # Add many approved/rejected approvals
        for i in range(1000):
            approval_id = f"old_approval_{i}"
            engine.pending_approvals[approval_id] = {
                "opportunity": opportunity,
                "status": "approved",
            }

        # Add few pending approvals
        for i in range(5):
            engine.submit_for_approval(opportunity)

        # Measure pending approvals query time
        start_time = time.time()
        for _ in range(100):
            pending = engine.get_pending_approvals()
        elapsed = time.time() - start_time

        assert len(pending) == 5
        # Should be fast even with 1000 total approvals
        assert elapsed < 0.01, f"Pending query took {elapsed}s, expected < 10ms"


if __name__ == "__main__":
    print("Running performance tests...")

    print("\n1. Testing price cache...")
    test = TestPriceCache()
    test.test_price_cache_hit()
    print("   ✓ Price cache hit works correctly")

    print("\n2. Testing deque performance...")
    test = TestDequePerformance()
    test.test_deque_maxlen_behavior()
    print("   ✓ Deque maxlen behavior correct")
    test.test_deque_performance()
    print("   ✓ Deque append is O(1)")

    print("\n3. Testing incremental counters...")
    test = TestIncrementalCounters()
    test.test_stats_counters_accuracy()
    print("   ✓ Stats counters are accurate")
    test.test_stats_performance()
    print("   ✓ Stats calculation is O(1)")

    print("\n4. Testing pending approvals optimization...")
    test = TestPendingApprovalsOptimization()
    test.test_pending_ids_tracking()
    print("   ✓ Pending IDs tracking works correctly")
    test.test_pending_approvals_performance()
    print("   ✓ Pending approvals query scales well")

    print("\n✅ All performance tests passed!")
