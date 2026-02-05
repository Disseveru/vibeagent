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

app = Flask(__name__)
CORS(app)

# Global agent instance
agent = None
avocado = None


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


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


def run_server(host='0.0.0.0', port=5000, debug=False):
    """Run the Flask server"""
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    run_server(port=port, debug=debug)
