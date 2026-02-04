"""
Example: Using VibeAgent programmatically for arbitrage
"""
from vibeagent.agent import VibeAgent
from vibeagent.avocado_integration import AvocadoIntegration

# Initialize the agent
agent = VibeAgent(network="ethereum")

# Scan for arbitrage opportunity
opportunity = agent.analyze_arbitrage_opportunity(
    token_pair=(
        "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",  # WETH
        "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"   # USDC
    ),
    dexes=["uniswap_v3", "sushiswap"]
)

# Generate strategy with AI
strategy = agent.generate_strategy_with_ai(opportunity)

print("Strategy generated:", strategy)

# Initialize Avocado integration
avocado = AvocadoIntegration(
    wallet_address="0xYourAvocadoWalletAddress",
    network="ethereum"
)

# Export for Avocado transaction builder
json_output = avocado.export_for_transaction_builder(
    strategy,
    filename="arbitrage_transaction.json"
)

print("\nTransaction batch exported!")
print("Import this into avocado.instadapp.io")
