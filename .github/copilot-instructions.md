# Copilot Coding Agent Instructions for VibeAgent

## Project Overview

VibeAgent is an AI-powered DeFi strategy generator that helps users create and execute sophisticated DeFi strategies including flashloan arbitrage and liquidations. It integrates with Instadapp Avocado multi-sig wallet and supports wallet connections via Reown AppKit (300+ wallets).

## Technology Stack

- **Language**: Python 3.8+
- **Web Framework**: Flask with Flask-CORS
- **Blockchain**: Web3.py for Ethereum, Polygon, and Arbitrum interactions
- **AI Integration**: OpenAI API for strategy generation
- **Frontend**: Server-rendered HTML templates with Jinja2
- **Wallet Integration**: Reown AppKit (via static JS, no build step)
- **Testing**: pytest with pytest-cov
- **Linting**: flake8, black, mypy

## Project Structure

```
vibeagent/
├── vibeagent/              # Main Python package
│   ├── __init__.py         # Package init, exports __version__
│   ├── agent.py            # Core VibeAgent class for DeFi analysis
│   ├── autonomous_scanner.py # Continuous opportunity monitoring
│   ├── avocado_integration.py # Instadapp Avocado wallet integration
│   ├── cli.py              # Click-based CLI commands
│   ├── config.py           # AgentConfig class for configuration
│   ├── contract_abis.py    # Contract ABIs and addresses
│   ├── execution_engine.py # Transaction execution and approval queue
│   ├── logger.py           # VibeLogger for audit trail
│   ├── web_interface.py    # Flask API endpoints
│   ├── static/             # Static assets (JS, icons, manifest)
│   │   └── reown-wallet.js # Wallet connection logic (plain JS)
│   └── templates/          # Jinja2 HTML templates
│       └── index.html      # Main web interface
├── contracts/              # Solidity smart contract templates
├── docs/                   # Documentation files
├── examples/               # Usage examples
├── test_vibeagent.py       # Quick verification script
├── test_autonomous.py      # pytest test suite
├── pyproject.toml          # Project config (deps, black, mypy settings)
├── requirements.txt        # Production dependencies
├── .env.example            # Environment variable template
└── render.yaml             # Render.com deployment config
```

## Setup and Development

### Install Dependencies

```bash
# Install all dependencies including dev tools
pip install -e ".[dev]"
```

### Configure Environment

```bash
cp .env.example .env
# Edit .env with your RPC URLs and API keys
```

Required environment variables:
- `ETHEREUM_RPC_URL` - Ethereum mainnet RPC (Alchemy/Infura)
- `POLYGON_RPC_URL` - Polygon RPC
- `ARBITRUM_RPC_URL` - Arbitrum RPC
- `OPENAI_API_KEY` - Optional, for AI-enhanced strategies

### Run the Web Interface

```bash
python -m vibeagent.cli web
# Opens at http://localhost:5000
```

### Run Tests

```bash
# Run the full pytest test suite
python -m pytest test_autonomous.py -v

# Run quick verification script
python test_vibeagent.py

# Run tests with coverage
python -m pytest test_autonomous.py --cov=vibeagent --cov-report=html
```

### Linting

```bash
# Format code
black vibeagent/ --line-length 100

# Check style
flake8 vibeagent/

# Type checking
mypy vibeagent/
```

## Code Style and Conventions

### Python Style
- Line length: 100 characters (configured in `pyproject.toml`)
- Use black for formatting
- Follow PEP 8 guidelines
- Type hints are optional but encouraged

### Code Comments
- Docstrings use triple quotes with Args/Returns sections
- Minimal inline comments - code should be self-documenting
- TODO comments follow format: `# TODO: Description`

### Error Handling
- Use try/except blocks for external service calls (RPC, API)
- Log errors with `self.logger.error()` or `print()`
- Return graceful fallbacks (empty lists, None, default values)

## Security Considerations

### XSS Prevention
- When displaying dynamic content from APIs or user input, use `textContent` for text-only content instead of `innerHTML` to prevent script injection
- Use data attributes with `addEventListener` instead of inline `onclick` handlers for user/API data
- Example patterns from codebase:
  ```javascript
  // Good: Use textContent for displaying data
  resultElement.textContent = JSON.stringify(data, null, 2);
  
  // Good: Use data attributes for event handlers
  element.dataset.id = someId;
  element.addEventListener('click', handler);
  
  // Bad: innerHTML with dynamic content can enable XSS
  element.innerHTML = userProvidedContent;
  
  // Bad: Inline onclick with user data
  element.innerHTML = `<button onclick="fn('${userInput}')">`;
  ```

### Thread Safety
- Wallet connection state uses `threading.Lock` (`wallet_connections_lock`)
- Always acquire lock before accessing `wallet_connections` dictionary

### CORS
- Flask app enables CORS with default settings (see CORS initialization in `web_interface.py`)
- Consider restricting origins in production

## Key Modules

### VibeAgent (`agent.py`)
The core agent class that:
- Initializes Web3 connections to blockchain networks
- Analyzes arbitrage opportunities across DEXes
- Analyzes liquidation opportunities on lending protocols
- Generates AI-powered or template-based strategies

### AutonomousScanner (`autonomous_scanner.py`)
Background scanner that:
- Continuously monitors token pairs for opportunities
- Runs in a daemon thread with configurable interval
- Stores discovered opportunities in memory
- Integrates with ExecutionEngine for automated execution

### ExecutionEngine (`execution_engine.py`)
Handles transaction execution:
- Performs safety checks (profit threshold, gas limits, blacklist)
- Manages pending approval queue for manual mode
- Tracks execution history and statistics

### AgentConfig (`config.py`)
Configuration management:
- Loads from environment variables
- Default safety parameters: min profit $50, max gas 100 Gwei
- Supports runtime updates via `config.update(**kwargs)`

### AvocadoIntegration (`avocado_integration.py`)
Transaction building for Avocado wallet:
- Converts strategies to Avocado transaction batch format
- Encodes flash loan, swap, and liquidation calls
- Exports JSON for Avocado transaction builder

## API Endpoints

### Core Endpoints
- `POST /api/initialize` - Initialize agent with network and wallet
- `POST /api/scan/arbitrage` - Scan for arbitrage opportunities
- `POST /api/scan/liquidation` - Scan for liquidation opportunities
- `POST /api/strategy/export` - Export strategy for Avocado
- `POST /api/strategy/simulate` - Simulate strategy execution

### Wallet Endpoints
- `POST /api/wallet/connect` - Handle wallet connection
- `POST /api/wallet/disconnect` - Handle disconnection
- `GET /api/wallet/balance/<address>` - Get wallet balance
- `GET /api/wallet/state` - Get connection state

### Autonomous Scanner Endpoints
- `POST /api/autonomous/start` - Start scanner
- `POST /api/autonomous/stop` - Stop scanner
- `GET /api/autonomous/status` - Get scanner status
- `GET /api/autonomous/opportunities` - Get discovered opportunities
- `POST /api/autonomous/approve/<network>/<id>` - Approve transaction
- `POST /api/autonomous/reject/<network>/<id>` - Reject transaction

## Testing Patterns

Tests use pytest and follow class-based organization:

```python
class TestConfig:
    """Test configuration management"""
    
    def test_config_initialization(self):
        """Test that config initializes with defaults"""
        config = AgentConfig()
        assert config.min_profit_usd >= 0
```

### Test Setup
- Mock RPC URLs for testing: `os.environ["ETHEREUM_RPC_URL"] = "https://eth.llamarpc.com"`
- Use `/tmp/` for test log files
- Tests are independent and don't require real blockchain access

### Test Categories
- `TestConfig` - Configuration management
- `TestLogger` - Logging functionality
- `TestExecutionEngine` - Safety checks and approval queue
- `TestAutonomousScanner` - Scanner lifecycle and state

## Common Development Tasks

### Adding a New API Endpoint

1. Add route in `web_interface.py`:
   ```python
   @app.route("/api/my-endpoint", methods=["POST"])
   def my_endpoint():
       data = request.json
       # Process data
       return jsonify({"success": True, "data": result})
   ```

2. Add tests in `test_autonomous.py` if endpoint involves core logic

### Adding a New DEX

1. Add DEX address in `contract_abis.py` under `CONTRACT_ADDRESSES`
2. Add ABI for router if different from existing ones
3. Add price fetching method in `agent.py` (e.g., `_get_newdex_price()`)
4. Register DEX in `_get_dex_price()` method

### Adding a New Network

1. Add RPC URL to `.env.example`
2. Add network config in `contract_abis.py` `CONTRACT_ADDRESSES`
3. Update `_get_chain_id()` in `avocado_integration.py`
4. Add to `NETWORKS` in `static/reown-wallet.js`

## Deployment

### Local Development
```bash
python -m vibeagent.cli web
```

### Production (Render/Gunicorn)
```bash
gunicorn vibeagent.web_interface:app --bind 0.0.0.0:$PORT
```

The `render.yaml` provides configuration for Render.com deployment.

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure package is installed with `pip install -e .`
2. **RPC errors**: Check `.env` file has valid RPC URLs
3. **Test failures**: Tests mock RPC URLs and don't require live blockchain
4. **Web interface not loading**: Check port 5000 is available

### Debug Mode
```bash
FLASK_DEBUG=true python -m vibeagent.cli web
```
