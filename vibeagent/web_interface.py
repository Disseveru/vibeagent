"""
Flask Web Interface for VibeAgent
No-code interface for non-technical users
"""

from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
import json
import threading
from datetime import datetime
from vibeagent.agent import VibeAgent
from vibeagent.avocado_integration import AvocadoIntegration
from vibeagent.config import AgentConfig
from vibeagent.logger import VibeLogger
from vibeagent.autonomous_scanner import AutonomousScanner
from vibeagent import __version__

app = Flask(__name__)
CORS(app)

# Global agent instance
agent = None
avocado = None

# Global autonomous scanner
config = AgentConfig()
logger = VibeLogger(log_file=config.log_file, log_level=config.log_level)
autonomous_scanner = None

# Wallet connection state (thread-safe)
wallet_connections = {}
wallet_connections_lock = threading.Lock()


@app.route("/")
def index():
    """Main page"""
    return render_template("index.html")


@app.route("/health")
def health():
    """Health check endpoint for monitoring"""
    return jsonify({"status": "healthy", "service": "vibeagent", "version": __version__})


@app.route("/static/<path:path>")
def send_static(path):
    """Serve static files (manifest, service worker, icons)"""
    return send_from_directory("static", path)


@app.route("/api/initialize", methods=["POST"])
def initialize():
    """Initialize the agent with user configuration"""
    global agent, avocado

    data = request.json
    network = data.get("network", "ethereum")
    wallet_address = data.get("wallet_address")

    try:
        agent = VibeAgent(network=network)
        if wallet_address:
            avocado = AvocadoIntegration(wallet_address=wallet_address, network=network)

        return jsonify(
            {"success": True, "message": f"Agent initialized on {network}", "network": network}
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/scan/arbitrage", methods=["POST"])
def scan_arbitrage():
    """Scan for arbitrage opportunities"""
    if not agent:
        return jsonify({"error": "Agent not initialized"}), 400

    data = request.json
    token_a = data.get("token_a")
    token_b = data.get("token_b")
    dexes = data.get("dexes", ["uniswap_v3", "sushiswap"])

    try:
        opportunity = agent.analyze_arbitrage_opportunity(
            token_pair=(token_a, token_b), dexes=dexes
        )

        # Generate strategy
        opportunity = agent.generate_strategy_with_ai(opportunity)

        return jsonify({"success": True, "opportunity": opportunity})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/scan/liquidation", methods=["POST"])
def scan_liquidation():
    """Scan for liquidation opportunities"""
    if not agent:
        return jsonify({"error": "Agent not initialized"}), 400

    data = request.json
    protocol = data.get("protocol", "aave")
    account = data.get("account")

    try:
        opportunities = agent.analyze_liquidation_opportunity(protocol=protocol, account=account)

        # Generate strategies for each opportunity
        for opp in opportunities:
            agent.generate_strategy_with_ai(opp)

        return jsonify({"success": True, "opportunities": opportunities})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/strategy/export", methods=["POST"])
def export_strategy():
    """Export strategy for Avocado transaction builder"""
    if not avocado:
        return jsonify({"error": "Avocado integration not initialized"}), 400

    data = request.json
    strategy = data.get("strategy")

    try:
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"/tmp/avocado_tx_{timestamp}.json"

        # Export strategy
        json_output = avocado.export_for_transaction_builder(strategy, filename)

        return jsonify(
            {"success": True, "filename": filename, "transaction_batch": json.loads(json_output)}
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/strategy/simulate", methods=["POST"])
def simulate_strategy():
    """Simulate strategy execution"""
    if not avocado:
        return jsonify({"error": "Avocado integration not initialized"}), 400

    data = request.json
    strategy = data.get("strategy")

    try:
        simulation = avocado.create_simulation_data(strategy)

        return jsonify({"success": True, "simulation": simulation})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/strategies", methods=["GET"])
def get_strategies():
    """Get all generated strategies"""
    if not agent:
        return jsonify({"error": "Agent not initialized"}), 400

    return jsonify({"success": True, "strategies": agent.get_all_strategies()})


@app.route("/api/templates", methods=["GET"])
def get_templates():
    """Get strategy templates"""
    templates = {
        "arbitrage": {
            "name": "DEX Arbitrage",
            "description": "Find price differences between DEXes and profit from arbitrage",
            "parameters": [
                {"name": "token_a", "type": "address", "description": "First token address"},
                {"name": "token_b", "type": "address", "description": "Second token address"},
                {"name": "dexes", "type": "array", "description": "List of DEXes to check"},
            ],
        },
        "liquidation": {
            "name": "Lending Protocol Liquidation",
            "description": "Find and execute liquidations on lending protocols",
            "parameters": [
                {
                    "name": "protocol",
                    "type": "string",
                    "description": "Lending protocol (aave, compound)",
                },
                {
                    "name": "account",
                    "type": "address",
                    "description": "Account to liquidate (optional)",
                },
            ],
        },
    }

    return jsonify({"success": True, "templates": templates})


@app.route("/api/download/<filename>")
def download_file(filename):
    """Download generated transaction file"""
    filepath = f"/tmp/{filename}"
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return jsonify({"error": "File not found"}), 404


# Wallet Connection Endpoints (Reown AppKit Integration)


@app.route("/api/wallet/connect", methods=["POST"])
def wallet_connect():
    """Handle wallet connection from frontend"""
    data = request.json
    address = data.get("address")
    chain_id = data.get("chainId")

    if not address:
        return jsonify({"success": False, "error": "No address provided"}), 400

    try:
        # Store wallet connection state (thread-safe)
        with wallet_connections_lock:
            wallet_connections[address] = {
                "address": address,
                "chainId": chain_id,
                "connected_at": datetime.now().isoformat(),
            }

        logger.info(f"Wallet connected: {address} on chain {chain_id}")

        return jsonify(
            {
                "success": True,
                "message": "Wallet connected successfully",
                "address": address,
                "chainId": chain_id,
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/wallet/disconnect", methods=["POST"])
def wallet_disconnect():
    """Handle wallet disconnection"""
    data = request.json
    address = data.get("address")

    with wallet_connections_lock:
        if address and address in wallet_connections:
            del wallet_connections[address]
            logger.info(f"Wallet disconnected: {address}")

    return jsonify({"success": True, "message": "Wallet disconnected"})


@app.route("/api/wallet/balance/<address>", methods=["GET"])
def get_wallet_balance(address):
    """Get wallet balance from blockchain"""
    if not agent:
        return jsonify({"error": "Agent not initialized"}), 400

    try:
        # Use agent's web3 connection to get balance
        balance_wei = agent.web3.eth.get_balance(address)
        balance_eth = balance_wei / 1e18

        return jsonify(
            {
                "success": True,
                "address": address,
                "balance": balance_eth,
                "balance_wei": str(balance_wei),
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/wallet/transaction/<tx_hash>", methods=["GET"])
def get_transaction(tx_hash):
    """Get transaction details"""
    if not agent:
        return jsonify({"error": "Agent not initialized"}), 400

    try:
        tx = agent.web3.eth.get_transaction(tx_hash)
        receipt = agent.web3.eth.get_transaction_receipt(tx_hash)

        return jsonify(
            {
                "success": True,
                "transaction": {
                    "hash": tx_hash,
                    "from": tx["from"],
                    "to": tx["to"],
                    "value": str(tx["value"]),
                    "gas": tx["gas"],
                    "gasPrice": str(tx["gasPrice"]),
                    "status": receipt["status"] if receipt else None,
                    "blockNumber": receipt["blockNumber"] if receipt else None,
                },
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/wallet/state", methods=["GET"])
def get_wallet_state():
    """Get current wallet connection state"""
    with wallet_connections_lock:
        connections = list(wallet_connections.values())
    return jsonify({"success": True, "connections": connections})


# Autonomous Scanner Endpoints


@app.route("/api/autonomous/start", methods=["POST"])
def start_autonomous_scanner():
    """Start the autonomous scanner"""
    global autonomous_scanner

    try:
        if not autonomous_scanner:
            autonomous_scanner = AutonomousScanner(config, logger)

        autonomous_scanner.start()

        return jsonify(
            {
                "success": True,
                "message": "Autonomous scanner started",
                "status": autonomous_scanner.get_status(),
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/autonomous/stop", methods=["POST"])
def stop_autonomous_scanner():
    """Stop the autonomous scanner"""

    if not autonomous_scanner:
        return jsonify({"error": "Scanner not initialized"}), 400

    try:
        autonomous_scanner.stop()
        return jsonify({"success": True, "message": "Autonomous scanner stopped"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/autonomous/status", methods=["GET"])
def get_autonomous_status():
    """Get autonomous scanner status"""

    if not autonomous_scanner:
        return jsonify({"is_running": False, "message": "Scanner not initialized"})

    try:
        status = autonomous_scanner.get_status()
        return jsonify({"success": True, "status": status})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/autonomous/opportunities", methods=["GET"])
def get_opportunities():
    """Get discovered opportunities"""

    if not autonomous_scanner:
        return jsonify({"error": "Scanner not initialized"}), 400

    limit = request.args.get("limit", 20, type=int)

    try:
        opportunities = autonomous_scanner.get_opportunities(limit)
        return jsonify({"success": True, "opportunities": opportunities})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/autonomous/stats", methods=["GET"])
def get_execution_stats():
    """Get execution statistics"""

    if not autonomous_scanner:
        return jsonify({"error": "Scanner not initialized"}), 400

    try:
        stats = autonomous_scanner.get_execution_stats()
        return jsonify({"success": True, "stats": stats})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/autonomous/approvals", methods=["GET"])
def get_pending_approvals():
    """Get pending transaction approvals"""

    if not autonomous_scanner:
        return jsonify({"error": "Scanner not initialized"}), 400

    try:
        approvals = autonomous_scanner.get_pending_approvals()
        return jsonify({"success": True, "approvals": approvals})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/autonomous/approve/<network>/<approval_id>", methods=["POST"])
def approve_transaction(network, approval_id):
    """Approve a pending transaction"""

    if not autonomous_scanner:
        return jsonify({"error": "Scanner not initialized"}), 400

    try:
        success = autonomous_scanner.approve_transaction(network, approval_id)
        return jsonify(
            {
                "success": success,
                "message": "Transaction approved" if success else "Approval failed",
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/autonomous/reject/<network>/<approval_id>", methods=["POST"])
def reject_transaction(network, approval_id):
    """Reject a pending transaction"""

    if not autonomous_scanner:
        return jsonify({"error": "Scanner not initialized"}), 400

    try:
        success = autonomous_scanner.reject_transaction(network, approval_id)
        return jsonify(
            {
                "success": success,
                "message": "Transaction rejected" if success else "Rejection failed",
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/autonomous/config", methods=["GET", "POST"])
def manage_config():
    """Get or update configuration"""

    if request.method == "GET":
        return jsonify({"success": True, "config": config.to_dict()})

    # POST - update configuration
    try:
        data = request.json
        config.update(**data)

        # If scanner is running, update its config too
        if autonomous_scanner:
            autonomous_scanner.update_config(**data)

        return jsonify(
            {"success": True, "message": "Configuration updated", "config": config.to_dict()}
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/logs/transactions", methods=["GET"])
def get_transaction_logs():
    """Get transaction history from logs"""
    limit = request.args.get("limit", 100, type=int)

    try:
        logs = logger.get_transaction_history(limit)
        return jsonify({"success": True, "logs": logs})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


def run_server(host="0.0.0.0", port=5000, debug=False):
    """Run the Flask server"""
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    # Check for PORT environment variable (used by Render, Heroku, etc.)
    port = int(os.getenv("PORT", os.getenv("FLASK_PORT", 5000)))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    run_server(port=port, debug=debug)
