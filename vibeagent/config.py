"""
Configuration management for autonomous agent
"""

import os
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()


class AgentConfig:
    """Configuration for autonomous arbitrage agent"""

    def __init__(self):
        # Safety parameters
        self.min_profit_usd = float(os.getenv("MIN_PROFIT_USD", "50"))
        self.max_gas_price_gwei = float(os.getenv("MAX_GAS_PRICE_GWEI", "100"))
        self.max_transaction_value_usd = float(os.getenv("MAX_TRANSACTION_VALUE_USD", "10000"))

        # Autonomy settings
        self.autonomous_mode = os.getenv("AUTONOMOUS_MODE", "false").lower() == "true"
        self.require_manual_approval = (
            os.getenv("REQUIRE_MANUAL_APPROVAL", "true").lower() == "true"
        )

        # Scanning parameters
        self.scan_interval_seconds = int(os.getenv("SCAN_INTERVAL_SECONDS", "60"))
        self.networks = self._parse_list(os.getenv("ENABLED_NETWORKS", "ethereum,polygon,arbitrum"))

        # Token pairs to monitor
        self.monitored_token_pairs = self._load_token_pairs()

        # DEXes to check
        self.enabled_dexes = self._parse_list(os.getenv("ENABLED_DEXES", "uniswap_v3,sushiswap"))

        # Blacklisted addresses (tokens/contracts to avoid)
        self.blacklisted_addresses = self._parse_list(os.getenv("BLACKLISTED_ADDRESSES", ""))

        # Wallet configuration
        self.avocado_wallet_address = os.getenv("AVOCADO_WALLET_ADDRESS", "")

        # Logging
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_file = os.getenv("LOG_FILE", "vibeagent.log")

    def _parse_list(self, value: str) -> List[str]:
        """Parse comma-separated list from env var"""
        if not value:
            return []
        return [item.strip() for item in value.split(",") if item.strip()]

    @property
    def blacklisted_addresses(self) -> List[str]:
        """List of blacklisted addresses"""
        return self._blacklisted_addresses

    @blacklisted_addresses.setter
    def blacklisted_addresses(self, addresses: List[str]):
        """Update blacklist and maintain lowercase set for fast lookups"""
        self._blacklisted_addresses = addresses or []
        self._blacklisted_set = {addr.lower() for addr in self._blacklisted_addresses}

    def _load_token_pairs(self) -> List[tuple]:
        """Load token pairs to monitor from config"""
        # Common pairs on Ethereum mainnet
        default_pairs = [
            # WETH/USDC
            (
                "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
                "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
            ),
            # WETH/USDT
            (
                "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
                "0xdAC17F958D2ee523a2206206994597C13D831ec7",
            ),
            # WETH/DAI
            (
                "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
                "0x6B175474E89094C44Da98b954EedeAC495271d0F",
            ),
        ]
        return default_pairs

    def is_address_blacklisted(self, address: str) -> bool:
        """Check if an address is blacklisted"""
        return address.lower() in self._blacklisted_set

    def is_profitable(self, profit_usd: float) -> bool:
        """Check if profit meets minimum threshold"""
        return profit_usd >= self.min_profit_usd

    def is_gas_acceptable(self, gas_price_gwei: float) -> bool:
        """Check if gas price is within acceptable range"""
        return gas_price_gwei <= self.max_gas_price_gwei

    def to_dict(self) -> Dict[str, Any]:
        """Export configuration as dictionary"""
        return {
            "min_profit_usd": self.min_profit_usd,
            "max_gas_price_gwei": self.max_gas_price_gwei,
            "max_transaction_value_usd": self.max_transaction_value_usd,
            "autonomous_mode": self.autonomous_mode,
            "require_manual_approval": self.require_manual_approval,
            "scan_interval_seconds": self.scan_interval_seconds,
            "networks": self.networks,
            "monitored_token_pairs": len(self.monitored_token_pairs),
            "enabled_dexes": self.enabled_dexes,
            "blacklisted_addresses": len(self.blacklisted_addresses),
            "avocado_wallet_address": self.avocado_wallet_address,
        }

    def update(self, **kwargs):
        """Update configuration values"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
