"""
Core AI Agent for DeFi Strategy Generation
"""
import os
from typing import Dict, List, Optional, Any
from web3 import Web3
import openai
from dotenv import load_dotenv

load_dotenv()


class VibeAgent:
    """
    AI-powered agent for generating DeFi strategies including:
    - Flashloan arbitrage opportunities
    - Liquidation opportunities
    - Transaction building for Avocado multi-sig wallet
    """
    
    def __init__(self, network: str = "ethereum"):
        """
        Initialize the VibeAgent
        
        Args:
            network: Blockchain network (ethereum, polygon, arbitrum)
        """
        self.network = network
        self.web3 = self._initialize_web3(network)
        self.openai_client = self._initialize_openai()
        self.strategies = []
        
    def _initialize_web3(self, network: str) -> Web3:
        """Initialize Web3 connection based on network"""
        rpc_urls = {
            "ethereum": os.getenv("ETHEREUM_RPC_URL"),
            "polygon": os.getenv("POLYGON_RPC_URL"),
            "arbitrum": os.getenv("ARBITRUM_RPC_URL")
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
    
    def analyze_arbitrage_opportunity(
        self, 
        token_pair: tuple,
        dexes: List[str]
    ) -> Dict[str, Any]:
        """
        Analyze potential arbitrage opportunities across DEXes
        
        Args:
            token_pair: Tuple of (token_a, token_b) addresses
            dexes: List of DEX names to check (e.g., ['uniswap_v3', 'sushiswap'])
            
        Returns:
            Dictionary containing arbitrage opportunity details
        """
        token_a, token_b = token_pair
        
        # This would connect to DEX contracts and fetch prices
        # For now, returning a structure
        opportunity = {
            "type": "arbitrage",
            "token_pair": token_pair,
            "dexes": dexes,
            "estimated_profit_usd": 0,
            "flash_loan_required": True,
            "gas_estimate": 0,
            "strategy": None
        }
        
        # Simulate price checking
        print(f"Analyzing arbitrage for {token_a[:8]}.../{token_b[:8]}... across {dexes}")
        
        return opportunity
    
    def analyze_liquidation_opportunity(
        self,
        protocol: str,
        account: Optional[str] = None
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
        
        # This would query lending protocol contracts
        # For structure demonstration
        opportunity = {
            "type": "liquidation",
            "protocol": protocol,
            "account": account or "0x...",
            "collateral_token": "0x...",
            "debt_token": "0x...",
            "health_factor": 0.98,
            "estimated_profit_usd": 0,
            "flash_loan_required": True,
            "strategy": None
        }
        
        return opportunities
    
    def generate_strategy_with_ai(
        self,
        opportunity: Dict[str, Any]
    ) -> Dict[str, Any]:
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
        
        prompt = self._create_strategy_prompt(opportunity)
        
        try:
            # Use OpenAI to analyze and suggest strategy
            # In production, this would call the API
            print("Generating AI-powered strategy...")
            strategy = self._generate_template_strategy(opportunity)
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
    
    def _generate_template_strategy(
        self,
        opportunity: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate template strategy based on opportunity type"""
        opp_type = opportunity.get("type")
        
        if opp_type == "arbitrage":
            return {
                "steps": [
                    {
                        "action": "flash_loan",
                        "protocol": "aave_v3",
                        "token": opportunity["token_pair"][0],
                        "amount": "auto"
                    },
                    {
                        "action": "swap",
                        "dex": opportunity["dexes"][0],
                        "from": opportunity["token_pair"][0],
                        "to": opportunity["token_pair"][1]
                    },
                    {
                        "action": "swap",
                        "dex": opportunity["dexes"][1],
                        "from": opportunity["token_pair"][1],
                        "to": opportunity["token_pair"][0]
                    },
                    {
                        "action": "repay_flash_loan",
                        "protocol": "aave_v3"
                    }
                ],
                "slippage_tolerance": 0.5,
                "deadline": 300
            }
        
        elif opp_type == "liquidation":
            return {
                "steps": [
                    {
                        "action": "flash_loan",
                        "protocol": "aave_v3",
                        "token": opportunity["debt_token"],
                        "amount": "required_debt_amount"
                    },
                    {
                        "action": "liquidate",
                        "protocol": opportunity["protocol"],
                        "account": opportunity["account"],
                        "debt_token": opportunity["debt_token"],
                        "collateral_token": opportunity["collateral_token"]
                    },
                    {
                        "action": "swap",
                        "dex": "uniswap_v3",
                        "from": opportunity["collateral_token"],
                        "to": opportunity["debt_token"]
                    },
                    {
                        "action": "repay_flash_loan",
                        "protocol": "aave_v3"
                    }
                ],
                "liquidation_bonus": "auto",
                "slippage_tolerance": 1.0
            }
        
        return {}
    
    def get_all_strategies(self) -> List[Dict[str, Any]]:
        """Get all generated strategies"""
        return self.strategies
    
    def add_strategy(self, strategy: Dict[str, Any]):
        """Add a strategy to the agent's strategy list"""
        self.strategies.append(strategy)
