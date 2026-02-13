"""
Quick verification test for VibeAgent
"""

import sys
import os

# Test imports
try:
    from vibeagent.agent import VibeAgent
    from vibeagent.avocado_integration import AvocadoIntegration

    print("✓ Core modules imported successfully")
except Exception as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)

# Test agent initialization (without real RPC)
try:
    # Mock RPC URL for testing
    os.environ["ETHEREUM_RPC_URL"] = "https://eth.llamarpc.com"

    agent = VibeAgent(network="ethereum")
    print("✓ VibeAgent initialized")
except Exception as e:
    print(f"✗ Agent initialization error: {e}")
    sys.exit(1)

# Test arbitrage analysis
try:
    opportunity = agent.analyze_arbitrage_opportunity(
        token_pair=(
            "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
            "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        ),
        dexes=["uniswap_v3", "sushiswap"],
    )
    print("✓ Arbitrage analysis works")
    print(f"  Type: {opportunity['type']}")
    print(f"  DEXes: {opportunity['dexes']}")
except Exception as e:
    print(f"✗ Arbitrage analysis error: {e}")
    sys.exit(1)

# Test strategy generation
try:
    strategy = agent.generate_strategy_with_ai(opportunity)
    print("✓ Strategy generation works")
    print(f"  Steps: {len(strategy['strategy']['steps'])}")
except Exception as e:
    print(f"✗ Strategy generation error: {e}")
    sys.exit(1)

# Test Avocado integration
try:
    avocado = AvocadoIntegration(
        wallet_address="0x1234567890123456789012345678901234567890", network="ethereum"
    )
    print("✓ Avocado integration initialized")
except Exception as e:
    print(f"✗ Avocado integration error: {e}")
    sys.exit(1)

# Test transaction export
try:
    tx_batch = avocado.strategy_to_avocado_transactions(strategy["strategy"])
    print("✓ Transaction batch generation works")
    print(f"  Chain ID: {tx_batch['chainId']}")
    print(f"  Transactions: {len(tx_batch['transactions'])}")
except Exception as e:
    print(f"✗ Transaction export error: {e}")
    sys.exit(1)

# Test simulation
try:
    simulation = avocado.create_simulation_data(strategy["strategy"])
    print("✓ Simulation works")
    print(f"  Estimated Gas: {simulation['estimated_gas']:,} units")
except Exception as e:
    print(f"✗ Simulation error: {e}")
    sys.exit(1)

print("\n✅ All tests passed!")
print("\nVibeAgent is ready to use!")
print("Run 'vibeagent web' to start the web interface")
