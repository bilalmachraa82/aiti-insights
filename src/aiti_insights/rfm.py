"""
AITI Insights - Análise RFM (Segmentação de Clientes)
====================================================

Segmenta clientes por:
- Recency (R): Há quanto tempo compraram
- Frequency (F): Quantas vezes compram
- Monetary (M): Quanto gastam

Gera segmentos accionáveis: Champions, At Risk, Dormant, etc.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)


# Definição de segmentos RFM
RFM_SEGMENTS = {
    "Champions": {
        "r_range": (4, 5),
        "f_range": (4, 5),
        "m_range": (4, 5),
        "description": "Compraram recentemente, compram frequentemente, e gastam muito",
        "action": "Premiar, pedir referências, upsell premium",
        "color": "#2E7D32"  # Verde escuro
    },
    "Loyal": {
        "r_range": (3, 5),
        "f_range": (3, 5),
        "m_range": (3, 5),
        "description": "Bons clientes regulares",
        "action": "Manter relação, oferecer exclusivos",
        "color": "#4CAF50"  # Verde
    },
    "Potential Loyalist": {
        "r_range": (3, 5),
        "f_range": (1, 3),
        "m_range": (1, 3),
        "description": "Clientes recentes com potencial",
        "action": "Oferecer membership, recomendar outros produtos",
        "color": "#8BC34A"  # Verde claro
    },
    "New Customers": {
        "r_range": (4, 5),
        "f_range": (1, 1),
        "m_range": (1, 5),
        "description": "Compraram muito recentemente, primeira compra",
        "action": "Onboarding, oferta de boas-vindas",
        "color": "#03A9F4"  # Azul claro
    },
    "Promising": {
        "r_range": (3, 4),
        "f_range": (1, 2),
        "m_range": (1, 2),
        "description": "Compras recentes, baixa frequência",
        "action": "Criar engagement, oferecer promoções",
        "color": "#00BCD4"  # Cyan
    },
    "Need Attention": {
        "r_range": (2, 3),
        "f_range": (2, 3),
        "m_range": (2, 3),
        "description": "Valores médios em tudo, podem escapar",
        "action": "Reactivar interesse, oferta limitada",
        "color": "#FFC107"  # Amarelo
    },
    "About to Sleep": {
        "r_range": (2, 3),
        "f_range": (1, 2),
        "m_range": (1, 2),
        "description": "Abaixo da média, risco de perder",
        "action": "Partilhar valor, oferta personalizada",
        "color": "#FF9800"  # Laranja
    },
    "At Risk": {
        "r_range": (1, 2),
        "f_range": (3, 5),
        "m_range": (3, 5),
        "description": "Eram bons clientes, deixaram de comprar",
        "action": "Enviar campanha de reactivação, ligar",
        "color": "#F44336"  # Vermelho
    },
    "Hibernating": {
        "r_range": (1, 2),
        "f_range": (1, 2),
        "m_range": (1, 2),
        "description": "Última compra há muito tempo, baixo engagement",
        "action": "Oferta agressiva de reactivação",
        "color": "#9E9E9E"  # Cinza
    },
    "Lost": {
        "r_range": (1, 1),
        "f_range": (1, 5),
        "m_range": (1, 5),
        "description": "Não compram há muito tempo",
        "action": "Campanha de win-back ou ignorar",
        "color": "#607D8B"  # Cinza azulado
    }
}


class RFMAnalyzer:
    """
    Analisador RFM para segmentação de clientes.
    
    Exemplo:
        analyzer = RFMAnalyzer()
        rfm_df = analyzer.analyze(sales_df)
        segments = analyzer.get_segment_summary()
    """
    
    def __init__(
        self,
        r_bins: int = 5,
        f_bins: int = 5,
        m_bins: int = 5,
        reference_date: datetime = None
    ):
        """
        Args:
            r_bins: Número de bins para Recency (default 5 = quintis)
            f_bins: Número de bins para Frequency
            m_bins: Número de bins para Monetary
            reference_date: Data de referência (default = hoje)
        """
        self.r_bins = r_bins
        self.f_bins = f_bins
        self.m_bins = m_bins
        self.reference_date = reference_date or datetime.now()
        
        self.rfm_df = None
        self.segment_summary = None
    
    def analyze(
        self,
        sales_df: pd.DataFrame,
        customer_col: str = "cliente_id",
        date_col: str = "data",
        value_col: str = "valor"
    ) -> pd.DataFrame:
        """
        Calcula métricas RFM e segmenta clientes.
        
        Args:
            sales_df: DataFrame com vendas
            customer_col: Coluna com ID do cliente
            date_col: Coluna com data
            value_col: Coluna com valor
            
        Returns:
            DataFrame com métricas RFM por cliente
        """
        logger.info("Iniciando análise RFM...")
        
        df = sales_df.copy()
        df[date_col] = pd.to_datetime(df[date_col])
        
        # Calcular métricas por cliente
        rfm = df.groupby(customer_col).agg({
            date_col: "max",  # Data da última compra
            customer_col: "count",  # Frequência (número de transacções)
            value_col: "sum"  # Valor total
        }).reset_index(drop=True)
        
        # Renomear colunas
        rfm.columns = ["recency_date", "frequency", "monetary"]
        
        # Reobter cliente_id
        rfm["cliente_id"] = df.groupby(customer_col)[customer_col].first().values
        
        # Calcular recency em dias
        rfm["recency"] = (self.reference_date - pd.to_datetime(rfm["recency_date"])).dt.days
        
        # Calcular scores RFM (1-5)
        # Nota: Para recency, menor é melhor, então invertemos
        rfm["R"] = pd.qcut(
            rfm["recency"].rank(method="first"),
            q=self.r_bins,
            labels=range(self.r_bins, 0, -1)
        ).astype(int)
        
        rfm["F"] = pd.qcut(
            rfm["frequency"].rank(method="first"),
            q=self.f_bins,
            labels=range(1, self.f_bins + 1),
            duplicates="drop"
        ).astype(int)
        
        rfm["M"] = pd.qcut(
            rfm["monetary"].rank(method="first"),
            q=self.m_bins,
            labels=range(1, self.m_bins + 1),
            duplicates="drop"
        ).astype(int)
        
        # Criar score RFM combinado
        rfm["RFM_Score"] = rfm["R"].astype(str) + rfm["F"].astype(str) + rfm["M"].astype(str)
        
        # Atribuir segmentos
        rfm["segment"] = rfm.apply(self._assign_segment, axis=1)
        
        # Adicionar informação do segmento
        rfm["segment_action"] = rfm["segment"].map(
            lambda s: RFM_SEGMENTS.get(s, {}).get("action", "Analisar caso a caso")
        )
        
        self.rfm_df = rfm
        
        # Calcular resumo por segmento
        self._calculate_segment_summary()
        
        logger.info(f"Análise RFM concluída para {len(rfm)} clientes")
        
        return rfm
    
    def _assign_segment(self, row) -> str:
        """Atribui segmento baseado nos scores RFM."""
        r, f, m = row["R"], row["F"], row["M"]
        
        for segment_name, criteria in RFM_SEGMENTS.items():
            r_min, r_max = criteria["r_range"]
            f_min, f_max = criteria["f_range"]
            m_min, m_max = criteria["m_range"]
            
            if (r_min <= r <= r_max and
                f_min <= f <= f_max and
                m_min <= m <= m_max):
                return segment_name
        
        return "Others"
    
    def _calculate_segment_summary(self):
        """Calcula resumo estatístico por segmento."""
        if self.rfm_df is None:
            return
        
        summary = self.rfm_df.groupby("segment").agg({
            "cliente_id": "count",
            "recency": "mean",
            "frequency": "mean",
            "monetary": ["mean", "sum"]
        }).round(2)
        
        summary.columns = ["count", "avg_recency_days", "avg_frequency", "avg_monetary", "total_monetary"]
        summary["percentage"] = (summary["count"] / summary["count"].sum() * 100).round(1)
        
        self.segment_summary = summary.reset_index()
    
    def get_segment_summary(self) -> pd.DataFrame:
        """Retorna resumo por segmento."""
        return self.segment_summary
    
    def get_segment_customers(self, segment: str) -> pd.DataFrame:
        """Retorna clientes de um segmento específico."""
        if self.rfm_df is None:
            raise ValueError("Execute analyze() primeiro")
        
        return self.rfm_df[self.rfm_df["segment"] == segment]
    
    def get_at_risk_customers(self) -> pd.DataFrame:
        """Retorna clientes em risco (At Risk + Hibernating)."""
        if self.rfm_df is None:
            raise ValueError("Execute analyze() primeiro")
        
        risk_segments = ["At Risk", "Hibernating", "About to Sleep"]
        return self.rfm_df[self.rfm_df["segment"].isin(risk_segments)]
    
    def get_reactivation_targets(self, min_value: float = 0) -> pd.DataFrame:
        """
        Retorna clientes para reactivação (já gastaram bem, pararam de comprar).
        
        Args:
            min_value: Valor mínimo histórico
        """
        if self.rfm_df is None:
            raise ValueError("Execute analyze() primeiro")
        
        targets = self.rfm_df[
            (self.rfm_df["segment"].isin(["At Risk", "Hibernating", "Lost"])) &
            (self.rfm_df["monetary"] >= min_value)
        ]
        
        return targets.sort_values("monetary", ascending=False)
    
    def get_champions(self) -> pd.DataFrame:
        """Retorna os melhores clientes (Champions + Loyal)."""
        if self.rfm_df is None:
            raise ValueError("Execute analyze() primeiro")
        
        return self.rfm_df[self.rfm_df["segment"].isin(["Champions", "Loyal"])]
    
    def get_insights(self) -> Dict:
        """Gera insights accionáveis da análise."""
        if self.rfm_df is None:
            raise ValueError("Execute analyze() primeiro")
        
        total_customers = len(self.rfm_df)
        total_value = self.rfm_df["monetary"].sum()
        
        champions = self.get_champions()
        at_risk = self.get_at_risk_customers()
        
        return {
            "total_clientes": total_customers,
            "valor_total": float(total_value),
            "champions": {
                "count": len(champions),
                "percentage": round(len(champions) / total_customers * 100, 1),
                "value": float(champions["monetary"].sum()),
                "value_percentage": round(champions["monetary"].sum() / total_value * 100, 1)
            },
            "at_risk": {
                "count": len(at_risk),
                "percentage": round(len(at_risk) / total_customers * 100, 1),
                "value": float(at_risk["monetary"].sum()),
                "value_percentage": round(at_risk["monetary"].sum() / total_value * 100, 1)
            },
            "insights": [
                f"Top 20% dos clientes representam {round(champions['monetary'].sum() / total_value * 100, 0)}% do valor",
                f"{len(at_risk)} clientes ({round(len(at_risk)/total_customers*100, 1)}%) precisam de reactivação",
                f"Recency médio dos Champions: {round(champions['recency'].mean(), 0)} dias",
                f"Recency médio dos At Risk: {round(at_risk['recency'].mean(), 0)} dias"
            ]
        }


def segment_customers(sales_df: pd.DataFrame, **kwargs) -> pd.DataFrame:
    """
    Função de conveniência para segmentação rápida.
    
    Args:
        sales_df: DataFrame com vendas
        **kwargs: Argumentos para RFMAnalyzer
        
    Returns:
        DataFrame com clientes segmentados
    """
    analyzer = RFMAnalyzer(**kwargs)
    return analyzer.analyze(sales_df)
