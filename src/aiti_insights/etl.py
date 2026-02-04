"""
AITI Insights - ETL (Extract, Transform, Load)
==============================================

Módulo para importação e normalização de dados de vendas.
Suporta CSV, Excel, e pode ser estendido para ERPs.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Optional, Union
import logging

logger = logging.getLogger(__name__)


class ETLProcessor:
    """
    Processador ETL para dados de vendas.
    
    Normaliza dados de diferentes fontes para formato padrão:
    - data: datetime
    - cliente_id: string
    - produto_id: string
    - quantidade: int
    - valor: float
    """
    
    # Mapeamento de nomes de colunas comuns
    COLUMN_MAPPINGS = {
        # Data
        "data": ["data", "date", "dt", "data_venda", "sale_date", "invoice_date", "data_factura"],
        # Cliente
        "cliente_id": ["cliente_id", "customer_id", "client_id", "cliente", "customer", "cod_cliente", "id_cliente"],
        # Produto  
        "produto_id": ["produto_id", "product_id", "item_id", "produto", "product", "cod_produto", "sku", "artigo"],
        # Quantidade
        "quantidade": ["quantidade", "quantity", "qty", "qtd", "qtde", "unidades"],
        # Valor
        "valor": ["valor", "value", "amount", "total", "preco_total", "valor_total", "revenue", "montante"],
    }
    
    def __init__(self):
        self.sales_df = None
        self.customers_df = None
        self.products_df = None
    
    def load_sales(self, path: Union[str, Path]) -> pd.DataFrame:
        """
        Carrega dados de vendas de CSV ou Excel.
        
        Args:
            path: Caminho para o ficheiro
            
        Returns:
            DataFrame normalizado com colunas padrão
        """
        path = Path(path)
        
        if not path.exists():
            raise FileNotFoundError(f"Ficheiro não encontrado: {path}")
        
        # Carregar baseado na extensão
        if path.suffix.lower() == ".csv":
            df = self._load_csv(path)
        elif path.suffix.lower() in [".xlsx", ".xls"]:
            df = self._load_excel(path)
        else:
            raise ValueError(f"Formato não suportado: {path.suffix}")
        
        # Normalizar colunas
        df = self._normalize_columns(df, "sales")
        
        # Validar dados obrigatórios
        self._validate_sales(df)
        
        # Transformações
        df = self._transform_sales(df)
        
        self.sales_df = df
        logger.info(f"Carregadas {len(df)} transacções de vendas")
        
        return df
    
    def load_customers(self, path: Union[str, Path]) -> pd.DataFrame:
        """Carrega dados de clientes."""
        path = Path(path)
        
        if path.suffix.lower() == ".csv":
            df = self._load_csv(path)
        else:
            df = self._load_excel(path)
        
        df = self._normalize_columns(df, "customers")
        self.customers_df = df
        
        logger.info(f"Carregados {len(df)} clientes")
        return df
    
    def load_products(self, path: Union[str, Path]) -> pd.DataFrame:
        """Carrega dados de produtos."""
        path = Path(path)
        
        if path.suffix.lower() == ".csv":
            df = self._load_csv(path)
        else:
            df = self._load_excel(path)
        
        df = self._normalize_columns(df, "products")
        self.products_df = df
        
        logger.info(f"Carregados {len(df)} produtos")
        return df
    
    def _load_csv(self, path: Path) -> pd.DataFrame:
        """Carrega CSV com detecção automática de encoding e separador."""
        # Tentar diferentes encodings
        for encoding in ["utf-8", "latin-1", "cp1252"]:
            for sep in [",", ";", "\t", "|"]:
                try:
                    df = pd.read_csv(path, encoding=encoding, sep=sep)
                    if len(df.columns) > 1:
                        return df
                except:
                    continue
        
        raise ValueError(f"Não foi possível ler o ficheiro CSV: {path}")
    
    def _load_excel(self, path: Path) -> pd.DataFrame:
        """Carrega Excel."""
        return pd.read_excel(path, engine="openpyxl")
    
    def _normalize_columns(self, df: pd.DataFrame, data_type: str) -> pd.DataFrame:
        """Normaliza nomes de colunas para formato padrão."""
        df.columns = df.columns.str.lower().str.strip()
        
        # Mapeamento específico por tipo
        if data_type == "sales":
            mapping = {
                "data": self.COLUMN_MAPPINGS["data"],
                "cliente_id": self.COLUMN_MAPPINGS["cliente_id"],
                "produto_id": self.COLUMN_MAPPINGS["produto_id"],
                "quantidade": self.COLUMN_MAPPINGS["quantidade"],
                "valor": self.COLUMN_MAPPINGS["valor"],
            }
        elif data_type == "customers":
            mapping = {
                "cliente_id": self.COLUMN_MAPPINGS["cliente_id"],
                "nome": ["nome", "name", "cliente_nome", "customer_name", "razao_social"],
                "segmento": ["segmento", "segment", "tipo", "type", "categoria"],
                "regiao": ["regiao", "region", "zona", "area", "distrito"],
            }
        elif data_type == "products":
            mapping = {
                "produto_id": self.COLUMN_MAPPINGS["produto_id"],
                "nome": ["nome", "name", "descricao", "description", "produto_nome"],
                "categoria": ["categoria", "category", "grupo", "group", "familia"],
                "preco_unitario": ["preco_unitario", "unit_price", "preco", "price", "pvp"],
            }
        else:
            return df
        
        # Aplicar mapeamento
        rename_map = {}
        for target, sources in mapping.items():
            for source in sources:
                if source in df.columns:
                    rename_map[source] = target
                    break
        
        return df.rename(columns=rename_map)
    
    def _validate_sales(self, df: pd.DataFrame):
        """Valida que dados de vendas têm colunas obrigatórias."""
        required = ["data", "cliente_id", "produto_id", "valor"]
        missing = [col for col in required if col not in df.columns]
        
        if missing:
            raise ValueError(
                f"Colunas obrigatórias em falta: {missing}. "
                f"Colunas disponíveis: {list(df.columns)}"
            )
    
    def _transform_sales(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplica transformações aos dados de vendas."""
        df = df.copy()
        
        # Converter data
        df["data"] = pd.to_datetime(df["data"], errors="coerce", dayfirst=True)
        
        # Remover linhas com data inválida
        invalid_dates = df["data"].isna().sum()
        if invalid_dates > 0:
            logger.warning(f"Removidas {invalid_dates} linhas com data inválida")
            df = df.dropna(subset=["data"])
        
        # Converter IDs para string
        df["cliente_id"] = df["cliente_id"].astype(str).str.strip()
        df["produto_id"] = df["produto_id"].astype(str).str.strip()
        
        # Converter valores numéricos
        df["valor"] = pd.to_numeric(df["valor"], errors="coerce").fillna(0)
        
        if "quantidade" in df.columns:
            df["quantidade"] = pd.to_numeric(df["quantidade"], errors="coerce").fillna(1).astype(int)
        else:
            df["quantidade"] = 1
        
        # Remover valores negativos ou zero
        df = df[df["valor"] > 0]
        
        # Ordenar por data
        df = df.sort_values("data").reset_index(drop=True)
        
        return df
    
    def get_summary(self) -> dict:
        """Retorna resumo dos dados carregados."""
        if self.sales_df is None:
            return {"error": "Nenhum dado carregado"}
        
        df = self.sales_df
        
        return {
            "transacoes": len(df),
            "clientes_unicos": df["cliente_id"].nunique(),
            "produtos_unicos": df["produto_id"].nunique(),
            "periodo": {
                "inicio": df["data"].min().strftime("%Y-%m-%d"),
                "fim": df["data"].max().strftime("%Y-%m-%d"),
                "dias": (df["data"].max() - df["data"].min()).days,
            },
            "valor_total": float(df["valor"].sum()),
            "ticket_medio": float(df["valor"].mean()),
        }
    
    def export_normalized(self, output_path: Union[str, Path]):
        """Exporta dados normalizados para CSV."""
        if self.sales_df is not None:
            self.sales_df.to_csv(output_path, index=False)
            logger.info(f"Dados exportados para {output_path}")


def load_demo_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Carrega dados de demonstração incluídos no pacote.
    
    Returns:
        Tuple com (sales_df, customers_df, products_df)
    """
    import importlib.resources as pkg_resources
    
    data_dir = Path(__file__).parent.parent.parent.parent / "data" / "demo"
    
    if not data_dir.exists():
        raise FileNotFoundError("Dados de demonstração não encontrados")
    
    etl = ETLProcessor()
    
    sales_df = etl.load_sales(data_dir / "vendas.csv")
    customers_df = etl.load_customers(data_dir / "clientes.csv")
    products_df = etl.load_products(data_dir / "produtos.csv")
    
    return sales_df, customers_df, products_df
