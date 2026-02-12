"""
Tests for MEV Bot functionality
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from vibeagent.mev_bot import MEVBot
from web3 import Web3

def test_mev_bot_initialization():
    """Test MEV bot can be initialized"""
    print("Testing MEV bot initialization...")
    
    # Mock Web3 instance
    web3 = Web3(Web3.HTTPProvider('https://eth.llamarpc.com'))
    
    mev_bot = MEVBot(web3, network="ethereum")
    
    assert mev_bot is not None
    assert mev_bot.network == "ethereum"
    assert mev_bot.risk_threshold == 0.7
    
    print("✓ MEV bot initialized successfully")


def test_mev_opportunity_detection():
    """Test MEV opportunity detection"""
    print("Testing MEV opportunity detection...")
    
    web3 = Web3(Web3.HTTPProvider('https://eth.llamarpc.com'))
    mev_bot = MEVBot(web3, network="ethereum")
    
    # Test token pair (WETH/USDC)
    token_pair = (
        "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
        "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
    )
    dexes = ["uniswap_v3", "sushiswap"]
    
    opportunities = mev_bot.detect_mev_opportunities(
        token_pair=token_pair,
        dexes=dexes,
        min_profit_usd=50.0
    )
    
    assert len(opportunities) > 0
    assert opportunities[0]["type"] == "mev_arbitrage"
    assert "risk_level" in opportunities[0]
    assert "protection_mechanisms" in opportunities[0]
    
    print(f"✓ Detected {len(opportunities)} MEV opportunity(ies)")
    print(f"  Risk Level: {opportunities[0]['risk_level']}")


def test_frontrunning_risk_analysis():
    """Test front-running risk analysis"""
    print("Testing front-running risk analysis...")
    
    web3 = Web3(Web3.HTTPProvider('https://eth.llamarpc.com'))
    mev_bot = MEVBot(web3, network="ethereum")
    
    # Test strategy
    strategy = {
        "type": "arbitrage",
        "estimated_profit_usd": 500,
        "steps": [
            {"action": "flash_loan"},
            {"action": "swap"},
            {"action": "swap"},
            {"action": "repay_flash_loan"}
        ]
    }
    
    analysis = mev_bot.analyze_frontrunning_risk(strategy)
    
    assert "mev_risk_score" in analysis
    assert "risk_level" in analysis
    assert analysis["risk_level"] in ["low", "medium", "high"]
    assert "recommendations" in analysis
    assert len(analysis["recommendations"]) > 0
    
    print(f"✓ Front-running analysis completed")
    print(f"  Risk Level: {analysis['risk_level']}")
    print(f"  Risk Score: {analysis['mev_risk_score']:.2%}")
    print(f"  Recommendations: {len(analysis['recommendations'])}")


def test_sandwich_risk_analysis():
    """Test sandwich attack risk analysis"""
    print("Testing sandwich attack risk analysis...")
    
    web3 = Web3(Web3.HTTPProvider('https://eth.llamarpc.com'))
    mev_bot = MEVBot(web3, network="ethereum")
    
    # Test strategy with high slippage
    strategy = {
        "type": "arbitrage",
        "estimated_profit_usd": 200,
        "steps": [
            {"action": "swap"},
            {"action": "swap"}
        ],
        "slippage_tolerance": 1.5  # High slippage
    }
    
    analysis = mev_bot.analyze_sandwich_risk(strategy, slippage_tolerance=1.5)
    
    assert "sandwich_risk_score" in analysis
    assert "risk_level" in analysis
    assert analysis["risk_level"] in ["low", "medium", "high"]
    assert "swap_count" in analysis
    assert analysis["swap_count"] == 2
    assert "recommendations" in analysis
    
    print(f"✓ Sandwich attack analysis completed")
    print(f"  Risk Level: {analysis['risk_level']}")
    print(f"  Risk Score: {analysis['sandwich_risk_score']:.2%}")
    print(f"  Swap Count: {analysis['swap_count']}")


def test_protection_strategy_generation():
    """Test protection strategy generation"""
    print("Testing protection strategy generation...")
    
    web3 = Web3(Web3.HTTPProvider('https://eth.llamarpc.com'))
    mev_bot = MEVBot(web3, network="ethereum")
    
    # Test opportunity
    opportunity = {
        "type": "arbitrage",
        "estimated_profit_usd": 300,
        "steps": [{"action": "swap"}, {"action": "swap"}]
    }
    
    # Test all protection levels
    for level in ["minimal", "standard", "maximum"]:
        protection = mev_bot.get_protection_strategy(opportunity, protection_level=level)
        
        assert "protection_level" in protection
        assert protection["protection_level"] == level
        assert "mechanisms" in protection
        assert len(protection["mechanisms"]) > 0
        assert "overall_mev_risk" in protection
        assert "warnings" in protection
        
        print(f"✓ {level.capitalize()} protection strategy generated")
        print(f"  Mechanisms: {len(protection['mechanisms'])}")
        print(f"  Overall Risk: {protection['overall_mev_risk']:.2%}")
        print(f"  Estimated Cost: ${protection['estimated_protection_cost_usd']}")


def test_mev_educational_content():
    """Test MEV educational content retrieval"""
    print("Testing MEV educational content...")
    
    web3 = Web3(Web3.HTTPProvider('https://eth.llamarpc.com'))
    mev_bot = MEVBot(web3, network="ethereum")
    
    education = mev_bot.get_mev_educational_content()
    
    assert "title" in education
    assert "summary" in education
    assert "attack_types" in education
    assert len(education["attack_types"]) >= 3  # Front-running, sandwich, back-running
    assert "protection_tools" in education
    assert "best_practices" in education
    assert "risk_levels" in education
    
    print(f"✓ Educational content retrieved")
    print(f"  Attack types covered: {len(education['attack_types'])}")
    print(f"  Protection tools: {len(education['protection_tools'])}")
    print(f"  Best practices: {len(education['best_practices'])}")


def test_risk_level_calculation():
    """Test risk level calculations for different scenarios"""
    print("Testing risk level calculations...")
    
    web3 = Web3(Web3.HTTPProvider('https://eth.llamarpc.com'))
    mev_bot = MEVBot(web3, network="ethereum")
    
    # Low profit, simple strategy
    low_risk_strategy = {
        "type": "arbitrage",
        "estimated_profit_usd": 30,
        "steps": [{"action": "swap"}]
    }
    
    # High profit, complex strategy
    high_risk_strategy = {
        "type": "arbitrage",
        "estimated_profit_usd": 2000,
        "steps": [{"action": "swap"}, {"action": "swap"}, {"action": "swap"}]
    }
    
    low_risk_analysis = mev_bot.analyze_frontrunning_risk(low_risk_strategy)
    high_risk_analysis = mev_bot.analyze_frontrunning_risk(high_risk_strategy)
    
    # High profit should have higher risk
    assert high_risk_analysis["mev_risk_score"] > low_risk_analysis["mev_risk_score"]
    
    print(f"✓ Risk level calculations working correctly")
    print(f"  Low risk strategy: {low_risk_analysis['mev_risk_score']:.2%}")
    print(f"  High risk strategy: {high_risk_analysis['mev_risk_score']:.2%}")


def run_all_tests():
    """Run all MEV bot tests"""
    print("=" * 60)
    print("Running MEV Bot Tests")
    print("=" * 60)
    
    tests = [
        test_mev_bot_initialization,
        test_mev_opportunity_detection,
        test_frontrunning_risk_analysis,
        test_sandwich_risk_analysis,
        test_protection_strategy_generation,
        test_mev_educational_content,
        test_risk_level_calculation,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            print(f"\n{test.__name__}")
            print("-" * 60)
            test()
            passed += 1
        except Exception as e:
            print(f"✗ Test failed: {e}")
            failed += 1
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
