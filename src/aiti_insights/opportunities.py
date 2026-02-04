"""
AITI Insights - Motor de Oportunidades
======================================

Combina análises (Apriori, RFM) para gerar oportunidades
accionáveis de cross-sell, upsell e reactivação.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)


class OpportunityEngine:
    """
    Motor que gera oportunidades de vendas baseado em:
    - Regras de associação (cross-sell)
    - Segmentação RFM (reactivação, churn risk)
    - Padrões de compra históricos
    
    Exemplo:
        engine = OpportunityEngine()
        opportunities = engine.generate(
            sales_df=sales_df,
            rules=apriori_rules,
            rfm_segments=rfm_df
        )
    """
    
    def __init__(
        self,
        min_confidence: float = 0.3,
        min_value: float = 100,
        reactivation_days: int = 90
    ):
        """
        Args:
            min_confidence: Confiança mínima para sugestões cross-sell
            min_value: Valor mínimo estimado para incluir oportunidade
            reactivation_days: Dias sem compra para considerar reactivação
        """
        self.min_confidence = min_confidence
        self.min_value = min_value
        self.reactivation_days = reactivation_days
        
        self.opportunities = []
    
    def generate(
        self,
        sales_df: pd.DataFrame,
        rules: List[Dict],
        rfm_segments: pd.DataFrame,
        customers_df: pd.DataFrame = None,
        products_df: pd.DataFrame = None
    ) -> List[Dict]:
        """
        Gera todas as oportunidades combinando análises.
        
        Args:
            sales_df: DataFrame com vendas históricas
            rules: Regras de associação do Apriori
            rfm_segments: DataFrame com segmentação RFM
            customers_df: DataFrame com info de clientes (opcional)
            products_df: DataFrame com info de produtos (opcional)
            
        Returns:
            Lista de oportunidades ordenadas por valor estimado
        """
        logger.info("Gerando oportunidades...")
        
        self.opportunities = []
        
        # 1. Oportunidades de Cross-Sell
        cross_sell = self._generate_cross_sell(sales_df, rules, products_df)
        self.opportunities.extend(cross_sell)
        logger.info(f"Geradas {len(cross_sell)} oportunidades cross-sell")
        
        # 2. Oportunidades de Reactivação
        reactivation = self._generate_reactivation(rfm_segments, sales_df, customers_df)
        self.opportunities.extend(reactivation)
        logger.info(f"Geradas {len(reactivation)} oportunidades reactivação")
        
        # 3. Clientes em Risco de Churn
        churn_risk = self._generate_churn_risk(rfm_segments, customers_df)
        self.opportunities.extend(churn_risk)
        logger.info(f"Geradas {len(churn_risk)} oportunidades churn risk")
        
        # Ordenar por valor estimado
        self.opportunities.sort(key=lambda x: x.get("valor_estimado", 0), reverse=True)
        
        # Filtrar por valor mínimo
        self.opportunities = [
            op for op in self.opportunities
            if op.get("valor_estimado", 0) >= self.min_value
        ]
        
        logger.info(f"Total: {len(self.opportunities)} oportunidades (filtradas por valor >= €{self.min_value})")
        
        return self.opportunities
    
    def _generate_cross_sell(
        self,
        sales_df: pd.DataFrame,
        rules: List[Dict],
        products_df: pd.DataFrame = None
    ) -> List[Dict]:
        """Gera oportunidades de cross-sell baseado em regras Apriori."""
        opportunities = []
        
        if not rules:
            return opportunities
        
        # Produtos por cliente
        customer_products = sales_df.groupby("cliente_id")["produto_id"].apply(set).to_dict()
        
        # Valor médio por produto
        avg_product_value = sales_df.groupby("produto_id")["valor"].mean().to_dict()
        
        # Para cada cliente, verificar regras aplicáveis
        for cliente_id, produtos in customer_products.items():
            for rule in rules:
                antecedent = set(rule["antecedent"])
                consequent = rule["consequent"][0]
                
                # Cliente tem o antecedente mas não o consequente
                if antecedent.issubset(produtos) and consequent not in produtos:
                    # Estimar valor
                    estimated_value = avg_product_value.get(consequent, 0)
                    
                    # Obter nome do produto se disponível
                    product_name = consequent
                    if products_df is not None and "nome" in products_df.columns:
                        match = products_df[products_df["produto_id"] == consequent]
                        if len(match) > 0:
                            product_name = match.iloc[0]["nome"]
                    
                    opportunities.append({
                        "tipo": "cross_sell",
                        "cliente_id": cliente_id,
                        "produto_sugerido": consequent,
                        "produto_nome": product_name,
                        "baseado_em": list(antecedent),
                        "probabilidade": rule["confidence"],
                        "lift": rule["lift"],
                        "valor_estimado": round(estimated_value, 2),
                        "acao": f"Oferecer {product_name}",
                        "prioridade": self._calculate_priority(rule["confidence"], estimated_value)
                    })
        
        # Remover duplicados (mesmo cliente + mesmo produto)
        seen = set()
        unique = []
        for op in opportunities:
            key = (op["cliente_id"], op["produto_sugerido"])
            if key not in seen:
                seen.add(key)
                unique.append(op)
        
        return unique
    
    def _generate_reactivation(
        self,
        rfm_df: pd.DataFrame,
        sales_df: pd.DataFrame,
        customers_df: pd.DataFrame = None
    ) -> List[Dict]:
        """Gera oportunidades de reactivação para clientes dormentes."""
        opportunities = []
        
        # Clientes dormentes/em risco
        dormant_segments = ["At Risk", "Hibernating", "Lost", "About to Sleep"]
        dormant = rfm_df[rfm_df["segment"].isin(dormant_segments)]
        
        for _, row in dormant.iterrows():
            cliente_id = row["cliente_id"]
            
            # Valor histórico
            historical_value = row["monetary"]
            
            # Estimar valor de reactivação (30% do valor histórico anualizado)
            estimated_value = historical_value * 0.3
            
            # Última compra
            last_purchase = row.get("recency_date", None)
            days_since = row["recency"]
            
            # Taxa de sucesso estimada baseada no segmento
            success_rates = {
                "About to Sleep": 0.4,
                "At Risk": 0.3,
                "Hibernating": 0.15,
                "Lost": 0.05
            }
            success_rate = success_rates.get(row["segment"], 0.2)
            
            # Obter nome do cliente se disponível
            customer_name = cliente_id
            if customers_df is not None and "nome" in customers_df.columns:
                match = customers_df[customers_df["cliente_id"] == str(cliente_id)]
                if len(match) > 0:
                    customer_name = match.iloc[0]["nome"]
            
            opportunities.append({
                "tipo": "reactivation",
                "cliente_id": cliente_id,
                "cliente_nome": customer_name,
                "segmento": row["segment"],
                "dias_sem_compra": days_since,
                "valor_historico": round(historical_value, 2),
                "valor_estimado": round(estimated_value * success_rate, 2),
                "probabilidade_sucesso": success_rate,
                "acao": row.get("segment_action", "Campanha de reactivação"),
                "prioridade": self._calculate_priority(success_rate, estimated_value)
            })
        
        return opportunities
    
    def _generate_churn_risk(
        self,
        rfm_df: pd.DataFrame,
        customers_df: pd.DataFrame = None
    ) -> List[Dict]:
        """Identifica clientes com alto risco de churn."""
        opportunities = []
        
        # Clientes que eram bons (F/M alto) mas R está a cair
        at_risk = rfm_df[
            (rfm_df["segment"] == "At Risk") |
            ((rfm_df["F"] >= 3) & (rfm_df["M"] >= 3) & (rfm_df["R"] <= 2))
        ]
        
        for _, row in at_risk.iterrows():
            cliente_id = row["cliente_id"]
            
            # Valor em risco = 50% do valor histórico
            value_at_risk = row["monetary"] * 0.5
            
            # Obter nome do cliente se disponível
            customer_name = cliente_id
            if customers_df is not None and "nome" in customers_df.columns:
                match = customers_df[customers_df["cliente_id"] == str(cliente_id)]
                if len(match) > 0:
                    customer_name = match.iloc[0]["nome"]
            
            # Calcular score de risco
            risk_score = (5 - row["R"]) / 4  # 0 a 1
            
            opportunities.append({
                "tipo": "churn_risk",
                "cliente_id": cliente_id,
                "cliente_nome": customer_name,
                "segmento": row["segment"],
                "rfm_score": row["RFM_Score"],
                "dias_sem_compra": row["recency"],
                "valor_em_risco": round(value_at_risk, 2),
                "valor_estimado": round(value_at_risk * 0.3, 2),  # 30% recuperável
                "risco_score": round(risk_score, 2),
                "acao": "Contacto urgente - cliente em risco",
                "prioridade": "alta" if risk_score > 0.7 else "media"
            })
        
        return opportunities
    
    def _calculate_priority(self, probability: float, value: float) -> str:
        """Calcula prioridade baseada em probabilidade e valor."""
        score = probability * (value / 1000)  # Normalizar valor
        
        if score > 0.5:
            return "alta"
        elif score > 0.2:
            return "media"
        else:
            return "baixa"
    
    def get_summary(self) -> Dict:
        """Retorna resumo das oportunidades."""
        if not self.opportunities:
            return {"error": "Nenhuma oportunidade gerada"}
        
        by_type = {}
        for op in self.opportunities:
            tipo = op["tipo"]
            if tipo not in by_type:
                by_type[tipo] = {"count": 0, "valor_total": 0}
            by_type[tipo]["count"] += 1
            by_type[tipo]["valor_total"] += op.get("valor_estimado", 0)
        
        return {
            "total_oportunidades": len(self.opportunities),
            "valor_total_estimado": sum(op.get("valor_estimado", 0) for op in self.opportunities),
            "por_tipo": by_type,
            "top_5": self.opportunities[:5]
        }
    
    def get_by_customer(self, cliente_id: str) -> List[Dict]:
        """Retorna oportunidades para um cliente específico."""
        return [op for op in self.opportunities if op["cliente_id"] == cliente_id]
    
    def get_by_type(self, tipo: str) -> List[Dict]:
        """Retorna oportunidades de um tipo específico."""
        return [op for op in self.opportunities if op["tipo"] == tipo]
    
    def get_high_priority(self) -> List[Dict]:
        """Retorna oportunidades de alta prioridade."""
        return [op for op in self.opportunities if op.get("prioridade") == "alta"]


def generate_opportunities(
    sales_df: pd.DataFrame,
    rules: List[Dict],
    rfm_segments: pd.DataFrame,
    **kwargs
) -> List[Dict]:
    """
    Função de conveniência para geração rápida de oportunidades.
    """
    engine = OpportunityEngine(**kwargs)
    return engine.generate(sales_df, rules, rfm_segments)
