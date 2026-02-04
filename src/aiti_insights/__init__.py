"""
AITI Insights - Motor de Oportunidades Comerciais
=================================================

Sistema de análise preditiva que identifica oportunidades de vendas
escondidas nos dados históricos.

Funcionalidades:
- ETL para importação de dados (CSV/Excel)
- Análise Apriori para cross-sell
- Segmentação RFM de clientes
- Dashboard interactivo Streamlit
- Geração de relatórios semanais

Uso básico:
    from aiti_insights import AITIInsights
    
    engine = AITIInsights()
    engine.load_data("vendas.csv")
    oportunidades = engine.analyze()
"""

__version__ = "1.0.0"
__author__ = "AiParaTi"
__email__ = "info@aiparati.pt"

from .etl import ETLProcessor
from .apriori import AprioriAnalyzer
from .rfm import RFMAnalyzer
from .opportunities import OpportunityEngine

__all__ = [
    "ETLProcessor",
    "AprioriAnalyzer", 
    "RFMAnalyzer",
    "OpportunityEngine",
]


class AITIInsights:
    """
    Classe principal que orquestra todas as análises.
    
    Exemplo:
        engine = AITIInsights()
        engine.load_data("vendas.csv", "clientes.csv", "produtos.csv")
        oportunidades = engine.analyze()
        engine.generate_report("relatorio.html")
    """
    
    def __init__(self):
        self.etl = ETLProcessor()
        self.apriori = AprioriAnalyzer()
        self.rfm = RFMAnalyzer()
        self.opportunity_engine = OpportunityEngine()
        
        self.sales_df = None
        self.customers_df = None
        self.products_df = None
        self.opportunities = []
    
    def load_data(self, sales_path: str, customers_path: str = None, products_path: str = None):
        """Carrega dados de vendas, clientes e produtos."""
        self.sales_df = self.etl.load_sales(sales_path)
        
        if customers_path:
            self.customers_df = self.etl.load_customers(customers_path)
        
        if products_path:
            self.products_df = self.etl.load_products(products_path)
        
        return self
    
    def analyze(self) -> dict:
        """
        Executa todas as análises e retorna oportunidades.
        
        Returns:
            dict com regras_apriori, segmentos_rfm, e oportunidades
        """
        if self.sales_df is None:
            raise ValueError("Dados não carregados. Use load_data() primeiro.")
        
        # Análise Apriori
        regras = self.apriori.analyze(self.sales_df)
        
        # Análise RFM
        segmentos = self.rfm.analyze(self.sales_df)
        
        # Gerar oportunidades
        self.opportunities = self.opportunity_engine.generate(
            sales_df=self.sales_df,
            rules=regras,
            rfm_segments=segmentos,
            customers_df=self.customers_df,
            products_df=self.products_df
        )
        
        return {
            "regras_apriori": regras,
            "segmentos_rfm": segmentos,
            "oportunidades": self.opportunities,
            "metricas": self._calculate_metrics()
        }
    
    def _calculate_metrics(self) -> dict:
        """Calcula métricas resumidas."""
        total_potencial = sum(op.get("valor_estimado", 0) for op in self.opportunities)
        
        return {
            "total_oportunidades": len(self.opportunities),
            "potencial_total": total_potencial,
            "cross_sell": len([op for op in self.opportunities if op["tipo"] == "cross_sell"]),
            "reactivacao": len([op for op in self.opportunities if op["tipo"] == "reactivation"]),
            "churn_risk": len([op for op in self.opportunities if op["tipo"] == "churn_risk"]),
        }
