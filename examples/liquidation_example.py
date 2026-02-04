"""
Example: Using VibeAgent for liquidation hunting
"""
from vibeagent.agent import VibeAgent
from vibeagent.avocado_integration import AvocadoIntegration

# Initialize the agent
agent = VibeAgent(network="ethereum")

# Scan for liquidation opportunities
opportunities = agent.analyze_liquidation_opportunity(
    protocol="aave",
    account=None  # Scan all accounts
)

print(f"Found {len(opportunities)} liquidation opportunities")

# Generate strategy for the first opportunity
if opportunities:
    strategy = agent.generate_strategy_with_ai(opportunities[0])
    
    print("Strategy:", strategy)
    
    # Initialize Avocado integration
    avocado = AvocadoIntegration(
        wallet_address="0xYourAvocadoWalletAddress",
        network="ethereum"
    )
    
    # Simulate before exporting
    simulation = avocado.create_simulation_data(strategy)
    print("\nSimulation:")
    print(f"  Estimated Gas: {simulation['estimated_gas']:,} units")
    print(f"  Warnings: {simulation['warnings']}")
    
    # Export for Avocado
    json_output = avocado.export_for_transaction_builder(
        strategy,
        filename="liquidation_transaction.json"
    )
    
    print("\nTransaction batch exported!")
    print("Import this into avocado.instadapp.io")
