#!/usr/bin/env python3
"""
VibeAgent CLI - Command line interface for non-coders
Simple commands to generate DeFi strategies
"""
import click
import json
import os
from vibeagent.agent import VibeAgent
from vibeagent.avocado_integration import AvocadoIntegration
from colorama import init, Fore, Style

init(autoreset=True)


@click.group()
def cli():
    """VibeAgent - AI-powered DeFi strategy generator for Avocado multi-sig wallet"""
    pass


@cli.command()
@click.option('--network', default='ethereum', help='Network (ethereum/polygon/arbitrum)')
@click.option('--wallet', required=True, help='Your Avocado wallet address')
def init_agent(network, wallet):
    """Initialize the agent with your configuration"""
    click.echo(f"{Fore.CYAN}Initializing VibeAgent...{Style.RESET_ALL}")
    
    try:
        # Save configuration
        config = {
            'network': network,
            'wallet_address': wallet
        }
        
        with open('.vibeagent_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        click.echo(f"{Fore.GREEN}✓ Agent initialized successfully!{Style.RESET_ALL}")
        click.echo(f"Network: {network}")
        click.echo(f"Wallet: {wallet}")
        
    except Exception as e:
        click.echo(f"{Fore.RED}✗ Error: {str(e)}{Style.RESET_ALL}")


@cli.command()
@click.option('--token-a', required=True, help='First token address')
@click.option('--token-b', required=True, help='Second token address')
@click.option('--dexes', default='uniswap_v3,sushiswap', help='DEXes to check (comma-separated)')
@click.option('--output', default='arbitrage_strategy.json', help='Output filename')
def arbitrage(token_a, token_b, dexes, output):
    """Scan for arbitrage opportunities and generate strategy"""
    config = _load_config()
    if not config:
        return
    
    click.echo(f"{Fore.CYAN}Scanning for arbitrage opportunities...{Style.RESET_ALL}")
    
    try:
        # Initialize agent
        agent = VibeAgent(network=config['network'])
        avocado = AvocadoIntegration(
            wallet_address=config['wallet_address'],
            network=config['network']
        )
        
        # Analyze opportunity
        dex_list = [d.strip() for d in dexes.split(',')]
        opportunity = agent.analyze_arbitrage_opportunity(
            token_pair=(token_a, token_b),
            dexes=dex_list
        )
        
        # Generate strategy
        opportunity = agent.generate_strategy_with_ai(opportunity)
        
        # Export for Avocado
        json_output = avocado.export_for_transaction_builder(opportunity, output)
        
        click.echo(f"{Fore.GREEN}✓ Arbitrage strategy generated!{Style.RESET_ALL}")
        click.echo(f"Saved to: {output}")
        click.echo(f"\n{Fore.YELLOW}Next steps:{Style.RESET_ALL}")
        click.echo("1. Go to https://avocado.instadapp.io")
        click.echo("2. Open Transaction Builder")
        click.echo(f"3. Import {output}")
        click.echo("4. Review and execute with your multi-sig")
        
    except Exception as e:
        click.echo(f"{Fore.RED}✗ Error: {str(e)}{Style.RESET_ALL}")


@cli.command()
@click.option('--protocol', default='aave', help='Protocol (aave/compound)')
@click.option('--account', help='Specific account to check (optional)')
@click.option('--output', default='liquidation_strategy.json', help='Output filename')
def liquidation(protocol, account, output):
    """Scan for liquidation opportunities and generate strategy"""
    config = _load_config()
    if not config:
        return
    
    click.echo(f"{Fore.CYAN}Scanning for liquidation opportunities...{Style.RESET_ALL}")
    
    try:
        # Initialize agent
        agent = VibeAgent(network=config['network'])
        avocado = AvocadoIntegration(
            wallet_address=config['wallet_address'],
            network=config['network']
        )
        
        # Analyze opportunities
        opportunities = agent.analyze_liquidation_opportunity(
            protocol=protocol,
            account=account
        )
        
        if not opportunities:
            click.echo(f"{Fore.YELLOW}No liquidation opportunities found.{Style.RESET_ALL}")
            return
        
        # Generate strategy for first opportunity
        opportunity = agent.generate_strategy_with_ai(opportunities[0])
        
        # Export for Avocado
        json_output = avocado.export_for_transaction_builder(opportunity, output)
        
        click.echo(f"{Fore.GREEN}✓ Liquidation strategy generated!{Style.RESET_ALL}")
        click.echo(f"Found {len(opportunities)} opportunities")
        click.echo(f"Saved first strategy to: {output}")
        click.echo(f"\n{Fore.YELLOW}Next steps:{Style.RESET_ALL}")
        click.echo("1. Go to https://avocado.instadapp.io")
        click.echo("2. Open Transaction Builder")
        click.echo(f"3. Import {output}")
        click.echo("4. Review and execute with your multi-sig")
        
    except Exception as e:
        click.echo(f"{Fore.RED}✗ Error: {str(e)}{Style.RESET_ALL}")


@cli.command()
@click.option('--strategy-file', required=True, help='Strategy JSON file to simulate')
def simulate(strategy_file):
    """Simulate strategy execution before deploying"""
    config = _load_config()
    if not config:
        return
    
    click.echo(f"{Fore.CYAN}Simulating strategy...{Style.RESET_ALL}")
    
    try:
        # Load strategy
        with open(strategy_file, 'r') as f:
            strategy = json.load(f)
        
        # Initialize Avocado integration
        avocado = AvocadoIntegration(
            wallet_address=config['wallet_address'],
            network=config['network']
        )
        
        # Simulate
        simulation = avocado.create_simulation_data(strategy)
        
        click.echo(f"{Fore.GREEN}✓ Simulation complete!{Style.RESET_ALL}")
        click.echo(f"Network: {simulation['network']}")
        click.echo(f"Estimated Gas: {simulation['estimated_gas']:,} units")
        
        if simulation['warnings']:
            click.echo(f"\n{Fore.YELLOW}⚠️  Warnings:{Style.RESET_ALL}")
            for warning in simulation['warnings']:
                click.echo(f"  - {warning}")
        
    except Exception as e:
        click.echo(f"{Fore.RED}✗ Error: {str(e)}{Style.RESET_ALL}")


@cli.command()
def web():
    """Start the web interface (no-code GUI)"""
    click.echo(f"{Fore.CYAN}Starting web interface...{Style.RESET_ALL}")
    click.echo(f"Open your browser at: {Fore.GREEN}http://localhost:5000{Style.RESET_ALL}")
    click.echo(f"Press {Fore.YELLOW}Ctrl+C{Style.RESET_ALL} to stop")
    
    try:
        from vibeagent.web_interface import run_server
        run_server(debug=True)
    except KeyboardInterrupt:
        click.echo(f"\n{Fore.YELLOW}Web interface stopped.{Style.RESET_ALL}")
    except Exception as e:
        click.echo(f"{Fore.RED}✗ Error: {str(e)}{Style.RESET_ALL}")


def _load_config():
    """Load agent configuration"""
    if not os.path.exists('.vibeagent_config.json'):
        click.echo(f"{Fore.RED}✗ Agent not initialized. Run 'vibeagent init-agent' first.{Style.RESET_ALL}")
        return None
    
    with open('.vibeagent_config.json', 'r') as f:
        return json.load(f)


if __name__ == '__main__':
    cli()
