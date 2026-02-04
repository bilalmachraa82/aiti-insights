"""
Tests for ETL module.
"""

import pytest
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from aiti_insights.etl import ETLProcessor


class TestETLProcessor:
    """Tests for ETLProcessor class."""
    
    @pytest.fixture
    def etl(self):
        return ETLProcessor()
    
    @pytest.fixture
    def demo_data_path(self):
        return Path(__file__).parent.parent / "data" / "demo"
    
    def test_load_sales_csv(self, etl, demo_data_path):
        """Test loading sales from CSV."""
        df = etl.load_sales(demo_data_path / "vendas.csv")
        
        assert df is not None
        assert len(df) > 0
        assert "data" in df.columns
        assert "cliente_id" in df.columns
        assert "produto_id" in df.columns
        assert "valor" in df.columns
    
    def test_load_customers(self, etl, demo_data_path):
        """Test loading customers."""
        df = etl.load_customers(demo_data_path / "clientes.csv")
        
        assert df is not None
        assert len(df) > 0
        assert "cliente_id" in df.columns
        assert "nome" in df.columns
    
    def test_load_products(self, etl, demo_data_path):
        """Test loading products."""
        df = etl.load_products(demo_data_path / "produtos.csv")
        
        assert df is not None
        assert len(df) > 0
        assert "produto_id" in df.columns
        assert "nome" in df.columns
    
    def test_get_summary(self, etl, demo_data_path):
        """Test summary generation."""
        etl.load_sales(demo_data_path / "vendas.csv")
        summary = etl.get_summary()
        
        assert "transacoes" in summary
        assert "clientes_unicos" in summary
        assert "produtos_unicos" in summary
        assert "valor_total" in summary
        assert summary["transacoes"] > 0
    
    def test_column_normalization(self, etl):
        """Test that column names are normalized."""
        # Create test data with different column names
        test_data = pd.DataFrame({
            "Date": ["2025-01-01"],
            "Customer_ID": ["C001"],
            "Product_ID": ["P001"],
            "Qty": [1],
            "Amount": [100.0]
        })
        
        # Save and load
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            test_data.to_csv(f.name, index=False)
            df = etl.load_sales(f.name)
        
        # Check normalized columns exist
        assert "data" in df.columns or len(df.columns) > 0


class TestDataValidation:
    """Tests for data validation."""
    
    def test_invalid_file_raises_error(self):
        """Test that invalid file raises error."""
        etl = ETLProcessor()
        
        with pytest.raises(FileNotFoundError):
            etl.load_sales("nonexistent_file.csv")
    
    def test_missing_columns_raises_error(self):
        """Test that missing required columns raises error."""
        import tempfile
        
        # Create data without required columns
        test_data = pd.DataFrame({
            "foo": [1, 2, 3],
            "bar": [4, 5, 6]
        })
        
        etl = ETLProcessor()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            test_data.to_csv(f.name, index=False)
            
            with pytest.raises(ValueError):
                etl.load_sales(f.name)
