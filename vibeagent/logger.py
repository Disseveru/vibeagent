"""
Comprehensive logging system for autonomous agent
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


class VibeLogger:
    """Logger for VibeAgent operations"""

    def __init__(self, log_file: str = "vibeagent.log", log_level: str = "INFO"):
        self.log_file = log_file
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self._setup_logger()

        # Transaction log for audit trail
        self.transaction_log_file = "transactions.jsonl"

    def _setup_logger(self):
        """Setup logger with file and console handlers"""
        self.logger = logging.getLogger("vibeagent")
        self.logger.setLevel(self.log_level)

        # Remove existing handlers
        self.logger.handlers.clear()

        # File handler
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(self.log_level)
        file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.log_level)
        console_formatter = logging.Formatter("%(levelname)s - %(message)s")
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)

    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)

    def error(self, message: str):
        """Log error message"""
        self.logger.error(message)

    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)

    def log_scan_start(self, network: str, token_pairs: int):
        """Log start of scanning cycle"""
        self.info(f"Starting scan on {network} - checking {token_pairs} token pairs")

    def log_opportunity_found(self, opportunity: Dict[str, Any]):
        """Log discovered opportunity"""
        opp_type = opportunity.get("type", "unknown")
        profit = opportunity.get("estimated_profit_usd", 0)
        self.info(f"Opportunity found: {opp_type} - Estimated profit: ${profit:.2f}")

    def log_opportunity_rejected(self, reason: str, opportunity: Dict[str, Any]):
        """Log rejected opportunity with reason"""
        opp_type = opportunity.get("type", "unknown")
        self.warning(f"Opportunity rejected ({opp_type}): {reason}")

    def log_transaction_submitted(self, tx_hash: str, opportunity: Dict[str, Any]):
        """Log transaction submission"""
        self.info(f"Transaction submitted: {tx_hash}")
        self._log_transaction_to_file("submitted", tx_hash, opportunity)

    def log_transaction_success(self, tx_hash: str, profit: float):
        """Log successful transaction"""
        self.info(f"Transaction successful: {tx_hash} - Profit: ${profit:.2f}")
        self._log_transaction_to_file("success", tx_hash, {"profit": profit})

    def log_transaction_failure(self, tx_hash: Optional[str], error: str):
        """Log transaction failure"""
        self.error(f"Transaction failed: {tx_hash or 'N/A'} - Error: {error}")
        self._log_transaction_to_file("failed", tx_hash or "N/A", {"error": error})

    def log_safety_check_failed(self, check: str, details: Dict[str, Any]):
        """Log failed safety check"""
        self.warning(f"Safety check failed: {check} - {details}")

    def _log_transaction_to_file(self, status: str, tx_hash: str, data: Dict[str, Any]):
        """Log transaction to JSONL audit file"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "status": status,
            "tx_hash": tx_hash,
            "data": data,
        }

        try:
            with open(self.transaction_log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            self.error(f"Failed to write transaction log: {e}")

    def get_transaction_history(self, limit: int = 100) -> list:
        """Get transaction history from log file"""
        if not Path(self.transaction_log_file).exists():
            return []

        try:
            from collections import deque

            with open(self.transaction_log_file, "r") as f:
                # Use deque to efficiently get last N lines
                recent_lines = deque(f, maxlen=limit)
                return [json.loads(line) for line in recent_lines]
        except Exception as e:
            self.error(f"Failed to read transaction history: {e}")
            return []
