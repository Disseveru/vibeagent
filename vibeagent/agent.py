"""
Core AI Agent for DeFi Strategy Generation
"""

import os
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from web3 import Web3
import openai
from dotenv import load_dotenv
from .contract_abis import (
    ERC20_ABI,
    UNISWAP_V3_QUOTER_ABI,
    SUSHISWAP_ROUTER_ABI,
    AAVE_V3_POOL_ABI,
    CONTRACT_ADDRESSES,
)

load_dotenv()

# Common token addresses for price fetching
COMMON_TOKENS = {
    "ethereum": {
        "WETH": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
        "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
    },
    "polygon": {
        "WETH": "0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619",
        "USDC": "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
    },
    "arbitrum": {
        "WETH": "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1",
        "USDC": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
    },
}


class VibeAgent:
    """
    AI-powered agent for generating DeFi strategies including:
    - Flashloan arbitrage opportunities
    - Liquidation opportunities
    - Transaction building for Avocado multi-sig wallet
    """

    def __init__(self, network: str = "ethereum", price_cache_ttl: int = 30):
        """
        Initialize the VibeAgent

        Args:
            network: Blockchain network (ethereum, polygon, arbitrum)
            price_cache_ttl: Time-to-live for price cache in seconds (default: 30)
        """
        self.network = network
        self.web3 = self._initialize_web3(network)
        self.openai_client = self._initialize_openai()
        self.strategies = []
        self._token_cache = {}  # Cache for token decimals and symbols
        self._price_cache = {}  # Cache for DEX prices with TTL
        self._price_cache_ttl = price_cache_ttl

    def _initialize_web3(self, network: str) -> Web3:
        """Initialize Web3 connection based on network"""
        rpc_urls = {
            "ethereum": os.getenv("ETHEREUM_RPC_URL"),
            "polygon": os.getenv("POLYGON_RPC_URL"),
            "arbitrum": os.getenv("ARBITRUM_RPC_URL"),
        }

        rpc_url = rpc_urls.get(network)
        if not rpc_url:
            raise ValueError(f"Invalid network: {network}")

        return Web3(Web3.HTTPProvider(rpc_url))

    def _initialize_openai(self):
        """Initialize OpenAI client for AI-powered analysis"""
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            openai.api_key = api_key
            return openai
        return None

    def analyze_arbitrage_opportunity(self, token_pair: tuple, dexes: List[str]) -> Dict[str, Any]:
        """
        Analyze potential arbitrage opportunities across DEXes

        Args:
            token_pair: Tuple of (token_a, token_b) addresses
            dexes: List of DEX names to check (e.g., ['uniswap_v3', 'sushiswap'])

        Returns:
            Dictionary containing arbitrage opportunity details
        """
        token_a, token_b = token_pair

        print(f"Analyzing arbitrage for {token_a[:8]}.../{token_b[:8]}... across {dexes}")

        # Get token symbols for display
        symbol_a = self._get_token_symbol(token_a)
        symbol_b = self._get_token_symbol(token_b)
        print(f"Token pair: {symbol_a}/{symbol_b}")

        # Fetch prices from each DEX
        prices = {}
        for dex in dexes:
            price = self._get_dex_price(token_a, token_b, dex)
            if price:
                prices[dex] = price
                print(f"{dex}: {price:.6f} {symbol_b} per {symbol_a}")

        # Check if we have at least 2 prices to compare
        if len(prices) < 2:
            print("Not enough price data to analyze arbitrage")
            return {
                "type": "arbitrage",
                "token_pair": token_pair,
                "dexes": dexes,
                "prices": prices,
                "estimated_profit_usd": 0,
                "flash_loan_required": True,
                "gas_estimate": 0,
                "profitable": False,
                "strategy": None,
            }

        # Find best buy and sell prices
        min_price_dex = min(prices, key=prices.get)
        max_price_dex = max(prices, key=prices.get)
        min_price = prices[min_price_dex]
        max_price = prices[max_price_dex]

        # Calculate price difference percentage
        price_diff_pct = ((max_price - min_price) / min_price) * 100
        print(f"Price difference: {price_diff_pct:.2f}%")

        # Estimate profit with 10 ETH flash loan (example)
        flash_loan_amount = 10  # ETH

        # Rough profit calculation (simplified)
        # Buy token_b at min_price, sell at max_price
        profit_per_token = max_price - min_price
        estimated_profit = flash_loan_amount * profit_per_token

        # Estimate gas cost
        gas_estimate = 500000  # Complex arbitrage with flash loan
        gas_cost_usd = self._estimate_gas_cost(gas_estimate)

        # Calculate net profit
        net_profit = estimated_profit - gas_cost_usd
        profitable = net_profit > 50  # Min $50 profit threshold

        print(f"Estimated profit: ${estimated_profit:.2f}")
        print(f"Gas cost: ${gas_cost_usd:.2f}")
        print(f"Net profit: ${net_profit:.2f}")
        print(f"Profitable: {profitable}")

        opportunity = {
            "type": "arbitrage",
            "token_pair": token_pair,
            "token_symbols": (symbol_a, symbol_b),
            "dexes": dexes,
            "prices": prices,
            "buy_dex": min_price_dex,
            "sell_dex": max_price_dex,
            "buy_price": min_price,
            "sell_price": max_price,
            "price_difference_pct": price_diff_pct,
            "estimated_profit_usd": net_profit,
            "flash_loan_required": True,
            "flash_loan_amount": flash_loan_amount,
            "gas_estimate": gas_estimate,
            "gas_cost_usd": gas_cost_usd,
            "profitable": profitable,
            "strategy": None,
        }

        return opportunity

    def analyze_liquidation_opportunity(
        self, protocol: str, account: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Analyze liquidation opportunities in lending protocols

        Args:
            protocol: Lending protocol name (e.g., 'aave', 'compound')
            account: Optional specific account to check

        Returns:
            List of liquidation opportunities
        """
        opportunities = []

        print(f"Scanning {protocol} for liquidation opportunities...")

        # Currently only supports Aave V3
        if protocol not in ["aave", "aave_v3"]:
            print(f"Protocol {protocol} not yet supported. Only 'aave' is currently supported.")
            return opportunities

        try:
            pool_address = CONTRACT_ADDRESSES[self.network]["aave_v3_pool"]
            pool = self.web3.eth.contract(address=pool_address, abi=AAVE_V3_POOL_ABI)

            if account:
                # Check specific account
                account = Web3.to_checksum_address(account)
                opportunity = self._check_account_liquidation(pool, account, protocol)
                if opportunity:
                    opportunities.append(opportunity)
            else:
                # Note: In production, you would query a subgraph or event logs
                # to find accounts with loans. For now, we'll return a message
                print(
                    "Note: Scanning all accounts requires event log analysis "
                    "or subgraph queries."
                )
                print(
                    "Please provide a specific account address to check, "
                    "or implement event scanning."
                )

        except Exception as e:
            print(f"Error analyzing liquidations: {e}")

        if not opportunities:
            print("No liquidation opportunities found.")
        else:
            print(f"Found {len(opportunities)} liquidation opportunity(ies)")

        return opportunities

    def _check_account_liquidation(
        self, pool_contract, account: str, protocol: str
    ) -> Optional[Dict[str, Any]]:
        """Check if a specific account can be liquidated"""
        try:
            # Get user account data from Aave
            account_data = pool_contract.functions.getUserAccountData(account).call()

            total_collateral = account_data[0]
            total_debt = account_data[1]
            health_factor = account_data[5]

            # Health factor is in 18 decimals, < 1e18 means liquidatable
            health_factor_float = health_factor / (10**18)

            print(f"Account: {account}")
            print(
                f"Total Collateral: ${total_collateral / (10 ** 8):.2f}"
            )  # Aave uses 8 decimals for USD
            print(f"Total Debt: ${total_debt / (10 ** 8):.2f}")
            print(f"Health Factor: {health_factor_float:.4f}")

            # Can liquidate if health factor < 1.0
            if health_factor_float < 1.0:
                # Calculate potential profit (simplified)
                # Liquidation bonus is typically 5-10%
                liquidation_bonus = 0.05  # 5%
                max_liquidatable = total_debt * 0.5  # Can liquidate up to 50% of debt
                potential_profit = (max_liquidatable / (10**8)) * liquidation_bonus

                # Estimate gas cost
                gas_estimate = 400000
                gas_cost_usd = self._estimate_gas_cost(gas_estimate)
                net_profit = potential_profit - gas_cost_usd

                print("✓ Liquidation opportunity found!")
                print(f"Potential profit: ${potential_profit:.2f}")
                print(f"Gas cost: ${gas_cost_usd:.2f}")
                print(f"Net profit: {net_profit:.2f}")

                return {
                    "type": "liquidation",
                    "protocol": protocol,
                    "account": account,
                    "health_factor": health_factor_float,
                    "total_collateral_usd": total_collateral / (10**8),
                    "total_debt_usd": total_debt / (10**8),
                    "max_liquidatable_usd": max_liquidatable / (10**8),
                    "estimated_profit_usd": net_profit,
                    "liquidation_bonus_pct": liquidation_bonus * 100,
                    "flash_loan_required": True,
                    "gas_estimate": gas_estimate,
                    "gas_cost_usd": gas_cost_usd,
                    # Would need to query
                    "collateral_token": "0x0000000000000000000000000000000000000000",
                    # Would need to query
                    "debt_token": "0x0000000000000000000000000000000000000000",
                    "strategy": None,
                }
            else:
                print("Account is healthy (health factor >= 1.0)")
                return None

        except Exception as e:
            print(f"Error checking account {account}: {e}")
            return None

    def generate_strategy_with_ai(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use AI to generate optimal strategy for the opportunity

        Args:
            opportunity: Opportunity details from analysis

        Returns:
            Enhanced opportunity with AI-generated strategy
        """
        if not self.openai_client:
            print("OpenAI not configured, using template strategy")
            strategy = self._generate_template_strategy(opportunity)
            opportunity["strategy"] = strategy
            return opportunity

        print("Generating AI-powered strategy...")

        try:
            # Call OpenAI for strategy insights
            ai_insights = self._call_openai_for_strategy(opportunity)
            print(f"AI Insights: {ai_insights[:100]}...")

            # Generate template strategy with AI-enhanced parameters
            strategy = self._generate_template_strategy(opportunity)
            strategy["ai_insights"] = ai_insights
            strategy["generated_at"] = datetime.now().isoformat()

            opportunity["strategy"] = strategy

        except Exception as e:
            print(f"AI generation failed: {e}, using template")
            strategy = self._generate_template_strategy(opportunity)
            opportunity["strategy"] = strategy

        return opportunity

    def _create_strategy_prompt(self, opportunity: Dict[str, Any]) -> str:
        """Create prompt for AI strategy generation"""
        opp_type = opportunity.get("type", "unknown")
        return f"""
        Analyze this DeFi {opp_type} opportunity and suggest optimal execution strategy:
        {opportunity}

        Consider:
        1. Gas optimization
        2. Slippage protection
        3. Flash loan mechanics
        4. Risk mitigation
        """

    def _generate_template_strategy(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """Generate template strategy based on opportunity type"""
        opp_type = opportunity.get("type")

        if opp_type == "arbitrage":
            token_a, token_b = opportunity["token_pair"]
            buy_dex = opportunity.get("buy_dex", opportunity["dexes"][0])
            sell_dex = opportunity.get(
                "sell_dex",
                (
                    opportunity["dexes"][1]
                    if len(opportunity["dexes"]) > 1
                    else opportunity["dexes"][0]
                ),
            )

            token_symbols = opportunity.get("token_symbols", ["Token A", "Token B"])
            return {
                "type": "arbitrage",
                "description": (f"Arbitrage {token_symbols} between {buy_dex} and {sell_dex}"),
                "steps": [
                    {
                        "action": "flash_loan",
                        "protocol": "aave_v3",
                        "token": token_a,
                        "amount": str(opportunity.get("flash_loan_amount", 10)),
                    },
                    {
                        "action": "swap",
                        "dex": buy_dex,
                        "from": token_a,
                        "to": token_b,
                        "description": (
                            f"Buy {opportunity.get('token_symbols', ['', 'Token B'])[1]} "
                            f"on {buy_dex}"
                        ),
                    },
                    {
                        "action": "swap",
                        "dex": sell_dex,
                        "from": token_b,
                        "to": token_a,
                        "description": (
                            f"Sell {opportunity.get('token_symbols', ['', 'Token B'])[1]} "
                            f"on {sell_dex}"
                        ),
                    },
                    {
                        "action": "repay_flash_loan",
                        "protocol": "aave_v3",
                        "description": "Repay flash loan with fee",
                    },
                ],
                "estimated_profit_usd": opportunity.get("estimated_profit_usd", 0),
                "estimated_gas": opportunity.get("gas_estimate", 500000),
                "slippage_tolerance": 0.5,
                "deadline": 300,
                "risks": [
                    "Price slippage during execution",
                    "MEV/frontrunning risk",
                    "Gas price fluctuation",
                ],
            }

        elif opp_type == "liquidation":
            return {
                "type": "liquidation",
                "description": f"Liquidate position on {opportunity['protocol']}",
                "steps": [
                    {
                        "action": "flash_loan",
                        "protocol": "aave_v3",
                        "token": opportunity.get("debt_token", "0x0"),
                        "amount": "required_debt_amount",
                        "description": "Borrow debt token to repay",
                    },
                    {
                        "action": "liquidate",
                        "protocol": opportunity["protocol"],
                        "account": opportunity["account"],
                        "debt_token": opportunity.get("debt_token", "0x0"),
                        "collateral_token": opportunity.get("collateral_token", "0x0"),
                        "description": f"Liquidate account {opportunity['account'][:10]}...",
                    },
                    {
                        "action": "swap",
                        "dex": "uniswap_v3",
                        "from": opportunity.get("collateral_token", "0x0"),
                        "to": opportunity.get("debt_token", "0x0"),
                        "description": "Swap collateral to debt token",
                    },
                    {
                        "action": "repay_flash_loan",
                        "protocol": "aave_v3",
                        "description": "Repay flash loan",
                    },
                ],
                "estimated_profit_usd": opportunity.get("estimated_profit_usd", 0),
                "estimated_gas": opportunity.get("gas_estimate", 400000),
                "liquidation_bonus": opportunity.get("liquidation_bonus_pct", 5),
                "slippage_tolerance": 1.0,
                "risks": [
                    "Collateral price volatility",
                    "Liquidation may be front-run",
                    "Slippage on collateral swap",
                ],
            }

        return {}

    def get_all_strategies(self) -> List[Dict[str, Any]]:
        """Get all generated strategies"""
        return self.strategies

    def add_strategy(self, strategy: Dict[str, Any]):
        """Add a strategy to the agent's strategy list"""
        self.strategies.append(strategy)

    def _get_token_decimals(self, token_address: str) -> int:
        """Get token decimals from ERC20 contract"""
        cache_key = f"{token_address}_decimals"
        if cache_key in self._token_cache:
            return self._token_cache[cache_key]

        try:
            token_address = Web3.to_checksum_address(token_address)
            contract = self.web3.eth.contract(address=token_address, abi=ERC20_ABI)
            decimals = contract.functions.decimals().call()
            self._token_cache[cache_key] = decimals
            return decimals
        except Exception as e:
            print(f"Error getting decimals for {token_address}: {e}")
            return 18  # Default to 18 decimals

    def _get_token_symbol(self, token_address: str) -> str:
        """Get token symbol from ERC20 contract"""
        cache_key = f"{token_address}_symbol"
        if cache_key in self._token_cache:
            return self._token_cache[cache_key]

        try:
            token_address = Web3.to_checksum_address(token_address)
            contract = self.web3.eth.contract(address=token_address, abi=ERC20_ABI)
            symbol = contract.functions.symbol().call()
            self._token_cache[cache_key] = symbol
            return symbol
        except Exception as e:
            print(f"Error getting symbol for {token_address}: {e}")
            return "UNKNOWN"

    def _get_dex_price(self, token_a: str, token_b: str, dex: str) -> Optional[float]:
        """
        Get price quote from a DEX with caching for performance

        Args:
            token_a: Input token address
            token_b: Output token address
            dex: DEX name (uniswap_v3, sushiswap)

        Returns:
            Price as float (token_b per token_a) or None if error
        """
        try:
            token_a = Web3.to_checksum_address(token_a)
            token_b = Web3.to_checksum_address(token_b)

            # Check price cache first
            cache_key = f"{dex}_{token_a}_{token_b}"
            if cache_key in self._price_cache:
                cached_price, cached_time = self._price_cache[cache_key]
                # Check if cache is still valid (within TTL)
                if time.time() - cached_time < self._price_cache_ttl:
                    return cached_price

            # Get token decimals (these are already cached)
            decimals_a = self._get_token_decimals(token_a)
            decimals_b = self._get_token_decimals(token_b)

            # Use 1 token as test amount
            amount_in = 10**decimals_a

            price = None
            if dex == "uniswap_v3":
                price = self._get_uniswap_v3_price(
                    token_a, token_b, amount_in, decimals_a, decimals_b
                )
            elif dex == "sushiswap":
                price = self._get_sushiswap_price(
                    token_a, token_b, amount_in, decimals_a, decimals_b
                )
            else:
                print(f"Unknown DEX: {dex}")
                return None

            # Cache the price if successfully fetched
            if price is not None:
                self._price_cache[cache_key] = (price, time.time())

            return price

        except Exception as e:
            print(f"Error getting price from {dex}: {e}")
            return None

    def _get_uniswap_v3_price(
        self, token_a: str, token_b: str, amount_in: int, decimals_a: int, decimals_b: int
    ) -> Optional[float]:
        """Get price from Uniswap V3 Quoter"""
        try:
            quoter_address = CONTRACT_ADDRESSES[self.network]["uniswap_v3_quoter"]
            quoter = self.web3.eth.contract(address=quoter_address, abi=UNISWAP_V3_QUOTER_ABI)

            # Try 0.3% fee tier (most common)
            fee = 3000
            amount_out = quoter.functions.quoteExactInputSingle(
                token_a, token_b, fee, amount_in, 0
            ).call()

            # Convert to float price
            price = (amount_out / (10**decimals_b)) / (amount_in / (10**decimals_a))
            return price

        except Exception as e:
            print(f"Error querying Uniswap V3: {e}")
            return None

    def _get_sushiswap_price(
        self, token_a: str, token_b: str, amount_in: int, decimals_a: int, decimals_b: int
    ) -> Optional[float]:
        """Get price from SushiSwap Router"""
        try:
            router_address = CONTRACT_ADDRESSES[self.network]["sushiswap_router"]
            router = self.web3.eth.contract(address=router_address, abi=SUSHISWAP_ROUTER_ABI)

            # Get amounts out
            amounts = router.functions.getAmountsOut(amount_in, [token_a, token_b]).call()
            amount_out = amounts[1]

            # Convert to float price
            price = (amount_out / (10**decimals_b)) / (amount_in / (10**decimals_a))
            return price

        except Exception as e:
            print(f"Error querying SushiSwap: {e}")
            return None

    def _get_eth_price_usd(self) -> float:
        """
        Get current ETH price in USD from WETH/USDC pair on DEX

        Returns:
            ETH price in USD, or 2000 as fallback if unable to fetch
        """
        try:
            # Get WETH and USDC addresses for the current network
            if self.network not in COMMON_TOKENS:
                print(f"Network {self.network} not supported for price fetching, using fallback")
                return 2000.0

            weth_address = COMMON_TOKENS[self.network]["WETH"]
            usdc_address = COMMON_TOKENS[self.network]["USDC"]

            # Try to get price from Uniswap V3 first
            price = self._get_dex_price(weth_address, usdc_address, "uniswap_v3")

            # If that fails, try SushiSwap
            if price is None:
                price = self._get_dex_price(weth_address, usdc_address, "sushiswap")

            # If still no price, use conservative fallback
            if price is None:
                print("Unable to fetch ETH price from DEX, using fallback value of 2000")
                return 2000.0

            return price

        except Exception as e:
            print(f"Error fetching ETH price: {e}, using fallback value of 2000")
            return 2000.0

    def _estimate_gas_cost(self, gas_units: int = 500000) -> int:
        """Estimate gas cost in USD"""
        try:
            # Get current gas price
            gas_price = self.web3.eth.gas_price
            # Estimate ETH cost
            eth_cost = (gas_price * gas_units) / (10**18)
            # Get real-time ETH price from DEX
            eth_price_usd = self._get_eth_price_usd()
            return int(eth_cost * eth_price_usd)
        except Exception as e:
            print(f"Error estimating gas cost: {e}")
            return 50  # Default conservative estimate

    def _call_openai_for_strategy(self, opportunity: Dict[str, Any]) -> str:
        """Call OpenAI API for strategy generation with fallback"""
        if not self.openai_client:
            return "Using template strategy (OpenAI not configured)"

        try:
            prompt = self._create_strategy_prompt(opportunity)
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a DeFi strategy expert."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=500,
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return "Using template strategy (API call failed)"
