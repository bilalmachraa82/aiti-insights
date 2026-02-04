"""
Tests for Apriori module.
"""

import pytest
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from aiti_insights.apriori import AprioriAnalyzer, analyze_cross_sell


class TestAprioriAnalyzer:
    """Tests for AprioriAnalyzer class."""
    
    @pytest.fixture
    def sample_sales(self):
        """Create sample sales data with known patterns."""
        # Create data where A is often bought with B
        data = []
        
        # Pattern: P001 + P003 bought together frequently
        for i in range(50):
            data.append({"cliente_id": f"C{i:03d}", "produto_id": "P001", "data": "2025-01-01", "valor": 100})
            data.append({"cliente_id": f"C{i:03d}", "produto_id": "P003", "data": "2025-01-01", "valor": 50})
        
        # Some other transactions
        for i in range(50, 80):
            data.append({"cliente_id": f"C{i:03d}", "produto_id": "P002", "data": "2025-01-02", "valor": 75})
            data.append({"cliente_id": f"C{i:03d}", "produto_id": "P004", "data": "2025-01-02", "valor": 60})
        
        return pd.DataFrame(data)
    
    def test_analyze_finds_rules(self, sample_sales):
        """Test that analyzer finds association rules."""
        analyzer = AprioriAnalyzer(min_support=0.05, min_confidence=0.3)
        rules = analyzer.analyze(sample_sales)
        
        assert len(rules) > 0
        assert all("antecedent" in r for r in rules)
        assert all("consequent" in r for r in rules)
        assert all("confidence" in r for r in rules)
        assert all("lift" in r for r in rules)
    
    def test_finds_known_pattern(self, sample_sales):
        """Test that analyzer finds the P001->P003 pattern."""
        analyzer = AprioriAnalyzer(min_support=0.05, min_confidence=0.3)
        rules = analyzer.analyze(sample_sales)
        
        # Should find P001 -> P003 or P003 -> P001
        product_pairs = [(r["antecedent"], r["consequent"]) for r in rules]
        
        found = False
        for ant, cons in product_pairs:
            if ("P001" in ant and "P003" in cons) or ("P003" in ant and "P001" in cons):
                found = True
                break
        
        assert found, "Should find P001<->P003 association"
    
    def test_confidence_filter(self, sample_sales):
        """Test that confidence filter works."""
        analyzer = AprioriAnalyzer(min_support=0.01, min_confidence=0.9)
        rules = analyzer.analyze(sample_sales)
        
        for rule in rules:
            assert rule["confidence"] >= 0.9
    
    def test_get_recommendations(self, sample_sales):
        """Test recommendation generation."""
        analyzer = AprioriAnalyzer(min_support=0.05, min_confidence=0.3)
        analyzer.analyze(sample_sales)
        
        # Customer has P001, should recommend P003
        recs = analyzer.get_recommendations(["P001"], max_recommendations=5)
        
        # Check structure
        for rec in recs:
            assert "produto" in rec
            assert "probabilidade" in rec
    
    def test_empty_data_returns_empty(self):
        """Test that empty data returns empty rules."""
        analyzer = AprioriAnalyzer()
        empty_df = pd.DataFrame(columns=["cliente_id", "produto_id", "data", "valor"])
        rules = analyzer.analyze(empty_df)
        
        assert rules == []


class TestAnalyzeCrossSell:
    """Test convenience function."""
    
    def test_convenience_function(self):
        """Test analyze_cross_sell function."""
        data = pd.DataFrame({
            "cliente_id": ["C1", "C1", "C2", "C2"] * 10,
            "produto_id": ["P1", "P2", "P1", "P2"] * 10,
            "data": ["2025-01-01"] * 40,
            "valor": [100] * 40
        })
        
        rules = analyze_cross_sell(data, min_support=0.05)
        
        assert isinstance(rules, list)
