"""
Flask Web Interface for VibeAgent
No-code interface for non-technical users
"""
from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
import json
from datetime import datetime
from vibeagent.agent import VibeAgent
from vibeagent.avocado_integration import AvocadoIntegration
from vibeagent.wallet_connector import WalletConnector
from vibeagent.autonomous_executor import AutonomousExecutor
from vibeagent import __version__

app = Flask(__name__)
CORS(app)

# Global instances
agent = None
avocado = None
wallet_connector = None
autonomous_executor = None


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/health')
def health():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'service': 'vibeagent',
        'version': __version__
    })


@app.route('/static/<path:path>')
def send_static(path):
    """Serve static files (manifest, service worker, icons)"""
    return send_from_directory('static', path)


@app.route('/api/initialize', methods=['POST'])
def initialize():
    """Initialize the agent with user configuration"""
    global agent, avocado
    
    data = request.json
    network = data.get('network', 'ethereum')
    wallet_address = data.get('wallet_address')
    
    try:
        agent = VibeAgent(network=network)
        if wallet_address:
            avocado = AvocadoIntegration(wallet_address=wallet_address, network=network)
        
        return jsonify({
            'success': True,
            'message': f'Agent initialized on {network}',
            'network': network
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/scan/arbitrage', methods=['POST'])
def scan_arbitrage():
    """Scan for arbitrage opportunities"""
    if not agent:
        return jsonify({'error': 'Agent not initialized'}), 400
    
    data = request.json
    token_a = data.get('token_a')
    token_b = data.get('token_b')
    dexes = data.get('dexes', ['uniswap_v3', 'sushiswap'])
    
    try:
        opportunity = agent.analyze_arbitrage_opportunity(
            token_pair=(token_a, token_b),
            dexes=dexes
        )
        
        # Generate strategy
        opportunity = agent.generate_strategy_with_ai(opportunity)
        
        return jsonify({
            'success': True,
            'opportunity': opportunity
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/scan/liquidation', methods=['POST'])
def scan_liquidation():
    """Scan for liquidation opportunities"""
    if not agent:
        return jsonify({'error': 'Agent not initialized'}), 400
    
    data = request.json
    protocol = data.get('protocol', 'aave')
    account = data.get('account')
    
    try:
        opportunities = agent.analyze_liquidation_opportunity(
            protocol=protocol,
            account=account
        )
        
        # Generate strategies for each opportunity
        for opp in opportunities:
            agent.generate_strategy_with_ai(opp)
        
        return jsonify({
            'success': True,
            'opportunities': opportunities
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/strategy/export', methods=['POST'])
def export_strategy():
    """Export strategy for Avocado transaction builder"""
    if not avocado:
        return jsonify({'error': 'Avocado integration not initialized'}), 400
    
    data = request.json
    strategy = data.get('strategy')
    
    try:
        # Create filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'/tmp/avocado_tx_{timestamp}.json'
        
        # Export strategy
        json_output = avocado.export_for_transaction_builder(strategy, filename)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'transaction_batch': json.loads(json_output)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/strategy/simulate', methods=['POST'])
def simulate_strategy():
    """Simulate strategy execution"""
    if not avocado:
        return jsonify({'error': 'Avocado integration not initialized'}), 400
    
    data = request.json
    strategy = data.get('strategy')
    
    try:
        simulation = avocado.create_simulation_data(strategy)
        
        return jsonify({
            'success': True,
            'simulation': simulation
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/strategies', methods=['GET'])
def get_strategies():
    """Get all generated strategies"""
    if not agent:
        return jsonify({'error': 'Agent not initialized'}), 400
    
    return jsonify({
        'success': True,
        'strategies': agent.get_all_strategies()
    })


@app.route('/api/templates', methods=['GET'])
def get_templates():
    """Get strategy templates"""
    templates = {
        'arbitrage': {
            'name': 'DEX Arbitrage',
            'description': 'Find price differences between DEXes and profit from arbitrage',
            'parameters': [
                {'name': 'token_a', 'type': 'address', 'description': 'First token address'},
                {'name': 'token_b', 'type': 'address', 'description': 'Second token address'},
                {'name': 'dexes', 'type': 'array', 'description': 'List of DEXes to check'}
            ]
        },
        'liquidation': {
            'name': 'Lending Protocol Liquidation',
            'description': 'Find and execute liquidations on lending protocols',
            'parameters': [
                {'name': 'protocol', 'type': 'string', 'description': 'Lending protocol (aave, compound)'},
                {'name': 'account', 'type': 'address', 'description': 'Account to liquidate (optional)'}
            ]
        }
    }
    
    return jsonify({
        'success': True,
        'templates': templates
    })


@app.route('/api/download/<filename>')
def download_file(filename):
    """Download generated transaction file"""
    filepath = f'/tmp/{filename}'
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404


# ============================================================================
# WalletConnect Integration Endpoints
# ============================================================================

@app.route('/api/wallet/connect', methods=['POST'])
def connect_wallet():
    """Connect wallet via WalletConnect"""
    global wallet_connector, agent, autonomous_executor
    
    data = request.json
    wallet_address = data.get('wallet_address')
    network = data.get('network', 'ethereum')
    
    if not wallet_address:
        return jsonify({'error': 'Wallet address required'}), 400
    
    try:
        # Initialize wallet connector if not exists or network changed
        if not wallet_connector or wallet_connector.network != network:
            wallet_connector = WalletConnector(network=network)
        
        # Connect wallet
        result = wallet_connector.connect_wallet(wallet_address)
        
        if result['success']:
            # Initialize autonomous executor if agent exists
            if agent:
                autonomous_executor = AutonomousExecutor(agent, wallet_connector)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/wallet/disconnect', methods=['POST'])
def disconnect_wallet():
    """Disconnect wallet"""
    global wallet_connector, autonomous_executor
    
    if not wallet_connector:
        return jsonify({'error': 'No wallet connected'}), 400
    
    try:
        result = wallet_connector.disconnect_wallet()
        autonomous_executor = None
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/wallet/status', methods=['GET'])
def wallet_status():
    """Get wallet connection status"""
    if not wallet_connector:
        return jsonify({
            'connected': False,
            'message': 'No wallet connector initialized'
        })
    
    try:
        status = wallet_connector.get_connection_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({
            'connected': False,
            'error': str(e)
        }), 400


@app.route('/api/wallet/gas-check', methods=['POST'])
def check_gas():
    """Check gas balance for transaction"""
    if not wallet_connector or not wallet_connector.connected:
        return jsonify({'error': 'Wallet not connected'}), 400
    
    data = request.json
    estimated_gas = data.get('estimated_gas', 500000)
    
    try:
        result = wallet_connector.check_gas_balance(estimated_gas)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/wallet/networks', methods=['GET'])
def get_networks():
    """Get supported networks"""
    try:
        # Create temporary connector to get networks
        temp_connector = WalletConnector()
        networks = temp_connector.get_supported_networks()
        return jsonify({
            'success': True,
            'networks': networks
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/wallet/switch-network', methods=['POST'])
def switch_network():
    """Switch network"""
    global wallet_connector
    
    data = request.json
    network = data.get('network')
    
    if not network:
        return jsonify({'error': 'Network required'}), 400
    
    if not wallet_connector:
        return jsonify({'error': 'No wallet connected'}), 400
    
    try:
        result = wallet_connector.switch_network(network)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


# ============================================================================
# Autonomous Execution Endpoints
# ============================================================================

@app.route('/api/execute/arbitrage', methods=['POST'])
def execute_arbitrage():
    """Execute arbitrage opportunity with connected wallet"""
    if not autonomous_executor:
        return jsonify({'error': 'Autonomous executor not initialized. Connect wallet first.'}), 400
    
    data = request.json
    opportunity = data.get('opportunity')
    
    if not opportunity:
        return jsonify({'error': 'Opportunity data required'}), 400
    
    try:
        # Validate safety checks
        validation = autonomous_executor.validate_safety_checks(opportunity)
        
        if not validation['passed']:
            return jsonify({
                'success': False,
                'validation': validation,
                'error': 'Safety checks failed'
            }), 400
        
        # Execute arbitrage
        result = autonomous_executor.execute_arbitrage(opportunity)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/execute/scan', methods=['POST'])
def start_scan():
    """Start autonomous arbitrage scanning"""
    if not autonomous_executor:
        return jsonify({'error': 'Autonomous executor not initialized. Connect wallet first.'}), 400
    
    data = request.json
    token_pairs = data.get('token_pairs', [])
    dexes = data.get('dexes', ['uniswap_v3', 'sushiswap'])
    continuous = data.get('continuous', False)
    scan_interval = data.get('scan_interval', 60)
    
    if not token_pairs:
        return jsonify({'error': 'Token pairs required'}), 400
    
    try:
        # Start scanning in background (for demo, we'll do single scan)
        # In production, this would be a background task
        results = autonomous_executor.scan_and_execute_arbitrage(
            token_pairs=token_pairs,
            dexes=dexes,
            continuous=False,  # Single scan for web interface
            scan_interval=scan_interval
        )
        
        return jsonify({
            'success': True,
            'results': results,
            'stats': autonomous_executor.get_execution_stats()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/execute/stop', methods=['POST'])
def stop_scan():
    """Stop autonomous scanning"""
    if not autonomous_executor:
        return jsonify({'error': 'Autonomous executor not initialized'}), 400
    
    try:
        autonomous_executor.stop_scanning()
        return jsonify({
            'success': True,
            'message': 'Scanning stopped'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/execute/stats', methods=['GET'])
def execution_stats():
    """Get execution statistics"""
    if not autonomous_executor:
        return jsonify({
            'successful_executions': 0,
            'failed_executions': 0,
            'total_profit_usd': 0,
            'is_scanning': False
        })
    
    try:
        stats = autonomous_executor.get_execution_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/execute/validate', methods=['POST'])
def validate_opportunity():
    """Validate opportunity safety checks"""
    if not autonomous_executor:
        return jsonify({'error': 'Autonomous executor not initialized. Connect wallet first.'}), 400
    
    data = request.json
    opportunity = data.get('opportunity')
    
    if not opportunity:
        return jsonify({'error': 'Opportunity data required'}), 400
    
    try:
        validation = autonomous_executor.validate_safety_checks(opportunity)
        return jsonify(validation)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


def run_server(host='0.0.0.0', port=5000, debug=False):
    """Run the Flask server"""
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    # Check for PORT environment variable (used by Render, Heroku, etc.)
    port = int(os.getenv('PORT', os.getenv('FLASK_PORT', 5000)))
    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    run_server(port=port, debug=debug)
