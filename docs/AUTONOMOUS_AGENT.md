# Autonomous Agent Documentation

## Overview

The VibeAgent Autonomous Agent continuously monitors blockchain networks for arbitrage opportunities and can execute profitable transactions automatically through Avocado wallet integration.

## Features

### 🤖 Autonomous Scanning
- **Continuous Monitoring**: Scans configured token pairs across multiple DEXes at regular intervals
- **Multi-Network Support**: Monitors Ethereum, Polygon, and Arbitrum simultaneously
- **Real-Time Detection**: Identifies profitable arbitrage opportunities as they appear

### 🔒 Safety Checks
- **Minimum Profit Threshold**: Only executes trades above configured profit minimum
- **Gas Price Limits**: Prevents execution when gas prices are too high
- **Maximum Transaction Value**: Caps transaction sizes for risk management
- **Blacklist Support**: Avoids specified tokens or contracts
- **Health Monitoring**: Tracks execution success rates and errors

### ⚙️ Autonomy Levels
- **Manual Mode**: Discovers opportunities but requires approval for execution
- **Semi-Autonomous**: Auto-executes only approved opportunities
- **Fully Autonomous**: Automatically executes all profitable opportunities

### 📊 Real-Time Dashboard
- **Live Status Updates**: Shows scanner state and recent scans
- **Execution Statistics**: Tracks success rate and total profits
- **Opportunity History**: Displays recent discoveries with profitability indicators
- **Pending Approvals**: Lists transactions awaiting manual approval

### 🔐 Wallet Integration
- **Avocado Multi-Sig**: Secure transaction execution through Avocado wallet
- **Automatic Profit Transfer**: Sends profits back to your wallet
- **Transaction Logging**: Complete audit trail of all operations

## Configuration

### Environment Variables

```bash
# Autonomous Mode Settings
AUTONOMOUS_MODE=false                    # Enable/disable autonomous execution
REQUIRE_MANUAL_APPROVAL=true             # Require approval for transactions
SCAN_INTERVAL_SECONDS=60                 # Time between scans

# Safety Parameters
MIN_PROFIT_USD=50                        # Minimum profit threshold
MAX_GAS_PRICE_GWEI=100                   # Maximum acceptable gas price
MAX_TRANSACTION_VALUE_USD=10000          # Maximum transaction size

# Network Configuration
ENABLED_NETWORKS=ethereum,polygon,arbitrum  # Networks to monitor
ENABLED_DEXES=uniswap_v3,sushiswap         # DEXes to check

# Blacklist
BLACKLISTED_ADDRESSES=0x...,0x...        # Comma-separated addresses to avoid

# Logging
LOG_LEVEL=INFO                           # Logging verbosity
LOG_FILE=vibeagent.log                   # Log file location
```

### Web Interface Configuration

The autonomous agent can be configured through the web interface:

1. Navigate to the **Autonomous Mode** section
2. Enable/disable autonomous scanning with the checkbox
3. Configure safety parameters:
   - Minimum Profit (USD)
   - Max Gas Price (Gwei)
   - Scan Interval (seconds)
4. Toggle manual approval requirement
5. Click "Update Configuration" to apply changes

## Usage

### Starting the Autonomous Scanner

#### Via Web Interface

1. Open the web interface at `http://localhost:5000`
2. Initialize the agent with your network and wallet address
3. Go to the **Autonomous Mode** section
4. Check "Enable Autonomous Scanning"
5. Monitor the real-time status dashboard

#### Via API

```bash
# Start scanner
curl -X POST http://localhost:5000/api/autonomous/start

# Check status
curl http://localhost:5000/api/autonomous/status

# Stop scanner
curl -X POST http://localhost:5000/api/autonomous/stop
```

### Monitoring Operations

The web interface provides real-time updates every 5 seconds showing:

- **Scanner Status**: Running/stopped, last scan time, scan count
- **Execution Statistics**: Total executions, success rate, cumulative profit
- **Recent Opportunities**: List of discovered arbitrage opportunities
- **Pending Approvals**: Transactions awaiting your approval (if manual mode enabled)

### Approving Transactions

When manual approval is enabled:

1. Opportunities will appear in the "Pending Approvals" section
2. Review the opportunity details (type, network, estimated profit)
3. Click "✓ Approve" to execute or "✗ Reject" to decline

## API Endpoints

### Scanner Control

**Start Scanner**
```
POST /api/autonomous/start
```

**Stop Scanner**
```
POST /api/autonomous/stop
```

**Get Status**
```
GET /api/autonomous/status
```

### Data Retrieval

**Get Opportunities**
```
GET /api/autonomous/opportunities?limit=20
```

**Get Execution Stats**
```
GET /api/autonomous/stats
```

**Get Pending Approvals**
```
GET /api/autonomous/approvals
```

**Get Transaction Logs**
```
GET /api/logs/transactions?limit=100
```

### Configuration Management

**Get Configuration**
```
GET /api/autonomous/config
```

**Update Configuration**
```
POST /api/autonomous/config
Content-Type: application/json

{
  "autonomous_mode": true,
  "require_manual_approval": false,
  "min_profit_usd": 75,
  "max_gas_price_gwei": 80,
  "scan_interval_seconds": 45
}
```

### Transaction Management

**Approve Transaction**
```
POST /api/autonomous/approve/{network}/{approval_id}
```

**Reject Transaction**
```
POST /api/autonomous/reject/{network}/{approval_id}
```

## Safety Features

### Built-in Protections

1. **Profit Validation**: Only executes when estimated profit exceeds minimum threshold
2. **Gas Price Checks**: Prevents execution during network congestion
3. **Blacklist Filtering**: Automatically skips blacklisted tokens/addresses
4. **Transaction Limits**: Caps maximum transaction value
5. **Error Handling**: Graceful failure with detailed logging
6. **Rate Limiting**: Configurable scan intervals to avoid rate limits

### Risk Mitigation

- **Manual Approval Mode**: Review every transaction before execution
- **Comprehensive Logging**: Full audit trail in `vibeagent.log` and `transactions.jsonl`
- **Simulation Before Execution**: Estimates gas and validates strategy
- **Network-Specific Controls**: Independent execution engines per network
- **Reversible Operations**: All actions logged for accountability

## Logging and Monitoring

### Log Files

**Main Log** (`vibeagent.log`)
- Scanner operations
- Opportunity discoveries
- Execution attempts
- Errors and warnings

**Transaction Log** (`transactions.jsonl`)
- JSON Lines format for easy parsing
- Complete transaction history
- Status tracking (submitted, success, failed)
- Metadata for each transaction

### Log Levels

- **DEBUG**: Detailed internal operations
- **INFO**: General operational messages
- **WARNING**: Potential issues or rejected opportunities
- **ERROR**: Failures and exceptions

## Best Practices

### Initial Setup

1. **Start with Manual Mode**: Set `REQUIRE_MANUAL_APPROVAL=true` initially
2. **Use Conservative Thresholds**: Set high minimum profit to learn the system
3. **Test on Low-Value Networks**: Start with Polygon (lower gas costs)
4. **Monitor Closely**: Watch the first few executions carefully

### Production Operation

1. **Regular Monitoring**: Check the dashboard daily
2. **Review Logs**: Audit transaction logs weekly
3. **Update Blacklist**: Add problematic tokens as discovered
4. **Adjust Thresholds**: Optimize based on execution success rate
5. **Network Health**: Monitor gas prices and adjust limits accordingly

### Optimization

1. **Scan Interval**: Balance between responsiveness and rate limits
   - High-frequency: 30-60 seconds
   - Conservative: 120-300 seconds
2. **Profit Thresholds**: Adjust based on gas costs per network
   - Ethereum: $100+ recommended
   - Polygon/Arbitrum: $50+ acceptable
3. **Gas Limits**: Set based on historical network activity
   - Peak hours: Higher limits (100+ gwei)
   - Off-peak: Lower limits (50-80 gwei)

## Troubleshooting

### Scanner Won't Start

**Issue**: Scanner fails to start
**Solutions**:
- Check RPC URLs are configured correctly
- Verify network connectivity
- Ensure Avocado wallet address is valid
- Review logs for specific errors

### No Opportunities Found

**Issue**: Scanner runs but finds no opportunities
**Solutions**:
- Verify token pairs are correctly configured
- Check if thresholds are too restrictive
- Ensure DEX addresses are correct for the network
- Monitor market conditions (low volatility = fewer opportunities)

### Executions Failing

**Issue**: Transactions fail after submission
**Solutions**:
- Increase gas price limit
- Check Avocado wallet has sufficient balance
- Verify token approvals are set
- Review slippage tolerance settings

### High Error Rate

**Issue**: Many errors in logs
**Solutions**:
- Increase scan interval to reduce load
- Update RPC endpoint (may be rate-limited)
- Add problematic tokens to blacklist
- Check network connectivity

## Architecture

### Components

```
┌─────────────────────────────────────────────┐
│          Web Interface (Flask)              │
│  - Real-time status display                 │
│  - Configuration management                 │
│  - Approval interface                       │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│       Autonomous Scanner                    │
│  - Continuous monitoring                    │
│  - Multi-network coordination               │
│  - Opportunity discovery                    │
└──────────────────┬──────────────────────────┘
                   │
         ┌─────────┴─────────┐
         ▼                   ▼
┌──────────────────┐  ┌──────────────────┐
│  Execution       │  │  Configuration   │
│  Engine          │  │  & Logger        │
│  - Safety checks │  │  - Settings mgmt │
│  - Tx submission │  │  - Audit logging │
│  - Approval flow │  │  - History       │
└──────┬───────────┘  └──────────────────┘
       │
       ▼
┌──────────────────┐
│  Avocado Wallet  │
│  - Tx signing    │
│  - Multi-sig     │
│  - Execution     │
└──────────────────┘
```

### Data Flow

1. **Scanner** monitors token pairs across networks
2. **Agent** analyzes prices and detects arbitrage
3. **Execution Engine** validates opportunity with safety checks
4. **Approval Flow** (if manual mode):
   - Queues transaction
   - Displays in UI
   - Waits for approval
5. **Transaction Execution**:
   - Prepares Avocado transaction batch
   - Submits to wallet
   - Monitors confirmation
6. **Logging**:
   - Records all actions
   - Updates statistics
   - Displays in UI

## Security Considerations

### Private Key Management

- **Never commit private keys** to version control
- Use environment variables for sensitive data
- Leverage Avocado's multi-sig security
- Implement key rotation policies

### Network Security

- Use HTTPS for all RPC endpoints
- Validate all contract addresses
- Implement rate limiting
- Monitor for unusual activity

### Smart Contract Risks

- Test thoroughly on testnets first
- Start with small transaction values
- Use established protocols only (Aave, Uniswap, etc.)
- Keep blacklist updated

### Operational Security

- Secure server access
- Regular security audits
- Monitor logs for anomalies
- Implement alerting for failures

## Future Enhancements

- [ ] Machine learning for opportunity prediction
- [ ] Advanced risk scoring models
- [ ] Multi-hop arbitrage strategies
- [ ] Flash loan optimization
- [ ] MEV protection
- [ ] Cross-chain arbitrage
- [ ] Telegram/Discord notifications
- [ ] Advanced analytics dashboard
- [ ] Historical performance tracking
- [ ] Backtesting framework

## Support

For issues or questions:
- GitHub Issues: https://github.com/Disseveru/vibeagent/issues
- Documentation: https://github.com/Disseveru/vibeagent/docs

## License

See the main repository LICENSE file for details.
