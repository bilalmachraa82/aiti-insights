"""
AITI Insights - Análise Apriori (Cross-Sell)
============================================

Identifica regras de associação entre produtos:
"Clientes que compram A têm X% de probabilidade de comprar B"

Baseado no algoritmo Apriori para market basket analysis.
"""

import pandas as pd
import numpy as np
from typing import Optional, List, Dict
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class AprioriAnalyzer:
    """
    Analisador de regras de associação usando Apriori.
    
    Métricas calculadas:
    - Suporte: Frequência da combinação no dataset
    - Confiança: P(B|A) - Probabilidade de B dado A
    - Lift: Quanto a regra é melhor que random
    
    Exemplo:
        analyzer = AprioriAnalyzer(min_support=0.05, min_confidence=0.5)
        rules = analyzer.analyze(sales_df)
    """
    
    def __init__(
        self,
        min_support: float = 0.01,
        min_confidence: float = 0.3,
        min_lift: float = 1.0,
        max_rules: int = 100
    ):
        """
        Args:
            min_support: Suporte mínimo (0-1)
            min_confidence: Confiança mínima (0-1)
            min_lift: Lift mínimo (>=1 significa correlação positiva)
            max_rules: Número máximo de regras a retornar
        """
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.min_lift = min_lift
        self.max_rules = max_rules
        
        self.rules = []
        self.frequent_itemsets = {}
    
    def analyze(
        self,
        sales_df: pd.DataFrame,
        product_col: str = "produto_id",
        transaction_col: str = "cliente_id",
        date_col: str = "data"
    ) -> List[Dict]:
        """
        Executa análise Apriori nos dados de vendas.
        
        Args:
            sales_df: DataFrame com vendas
            product_col: Coluna com ID do produto
            transaction_col: Coluna para agrupar transacções (cliente ou factura)
            date_col: Coluna de data (para agrupar por período)
            
        Returns:
            Lista de regras de associação ordenadas por lift
        """
        logger.info("Iniciando análise Apriori...")
        
        # Criar "cestos de compras" - produtos comprados juntos
        baskets = self._create_baskets(sales_df, product_col, transaction_col)
        
        if len(baskets) < 10:
            logger.warning("Poucos cestos de compras para análise significativa")
            return []
        
        # Encontrar itemsets frequentes
        self.frequent_itemsets = self._find_frequent_itemsets(baskets)
        
        # Gerar regras de associação
        self.rules = self._generate_rules(baskets)
        
        # Filtrar e ordenar
        filtered_rules = [
            r for r in self.rules
            if r["confidence"] >= self.min_confidence
            and r["lift"] >= self.min_lift
        ]
        
        # Ordenar por lift (descendente)
        filtered_rules.sort(key=lambda x: x["lift"], reverse=True)
        
        # Limitar número de regras
        self.rules = filtered_rules[:self.max_rules]
        
        logger.info(f"Encontradas {len(self.rules)} regras de associação")
        
        return self.rules
    
    def _create_baskets(
        self,
        df: pd.DataFrame,
        product_col: str,
        transaction_col: str
    ) -> List[set]:
        """
        Cria cestos de compras agrupando produtos por transacção/cliente.
        """
        baskets = []
        
        # Agrupar por transacção
        grouped = df.groupby(transaction_col)[product_col].apply(set).reset_index()
        
        for _, row in grouped.iterrows():
            if len(row[product_col]) >= 2:  # Só cestos com 2+ produtos
                baskets.append(row[product_col])
        
        logger.info(f"Criados {len(baskets)} cestos de compras")
        return baskets
    
    def _find_frequent_itemsets(self, baskets: List[set]) -> Dict[frozenset, float]:
        """
        Encontra itemsets frequentes usando Apriori.
        """
        n_baskets = len(baskets)
        frequent = {}
        
        # Contar itens individuais
        item_counts = defaultdict(int)
        for basket in baskets:
            for item in basket:
                item_counts[item] += 1
        
        # Filtrar por suporte mínimo
        min_count = self.min_support * n_baskets
        frequent_items = {
            item for item, count in item_counts.items()
            if count >= min_count
        }
        
        # Guardar suporte de itens individuais
        for item in frequent_items:
            frequent[frozenset([item])] = item_counts[item] / n_baskets
        
        # Encontrar pares frequentes
        pair_counts = defaultdict(int)
        for basket in baskets:
            items = basket & frequent_items
            items_list = list(items)
            for i in range(len(items_list)):
                for j in range(i + 1, len(items_list)):
                    pair = frozenset([items_list[i], items_list[j]])
                    pair_counts[pair] += 1
        
        # Filtrar pares por suporte
        for pair, count in pair_counts.items():
            support = count / n_baskets
            if support >= self.min_support:
                frequent[pair] = support
        
        logger.info(f"Encontrados {len(frequent)} itemsets frequentes")
        return frequent
    
    def _generate_rules(self, baskets: List[set]) -> List[Dict]:
        """
        Gera regras de associação a partir dos itemsets frequentes.
        """
        rules = []
        n_baskets = len(baskets)
        
        # Para cada par frequente, gerar regras A->B e B->A
        for itemset, support in self.frequent_itemsets.items():
            if len(itemset) != 2:
                continue
            
            items = list(itemset)
            
            for i in range(2):
                antecedent = frozenset([items[i]])
                consequent = frozenset([items[1-i]])
                
                # Calcular confiança: P(B|A) = support(A,B) / support(A)
                support_antecedent = self.frequent_itemsets.get(antecedent, 0)
                support_consequent = self.frequent_itemsets.get(consequent, 0)
                
                if support_antecedent == 0:
                    continue
                
                confidence = support / support_antecedent
                
                # Calcular lift: confidence / support(B)
                if support_consequent == 0:
                    continue
                    
                lift = confidence / support_consequent
                
                rules.append({
                    "antecedent": list(antecedent),
                    "consequent": list(consequent),
                    "support": round(support, 4),
                    "confidence": round(confidence, 4),
                    "lift": round(lift, 2),
                    "count": int(support * n_baskets)
                })
        
        return rules
    
    def get_recommendations(
        self,
        customer_products: List[str],
        max_recommendations: int = 5
    ) -> List[Dict]:
        """
        Dado os produtos que um cliente compra, sugere outros produtos.
        
        Args:
            customer_products: Lista de produtos que o cliente já compra
            max_recommendations: Máximo de recomendações
            
        Returns:
            Lista de produtos recomendados com probabilidade
        """
        recommendations = {}
        customer_set = set(customer_products)
        
        for rule in self.rules:
            antecedent = set(rule["antecedent"])
            consequent = rule["consequent"][0]
            
            # Se cliente compra o antecedente mas não o consequente
            if antecedent.issubset(customer_set) and consequent not in customer_set:
                if consequent not in recommendations:
                    recommendations[consequent] = {
                        "produto": consequent,
                        "probabilidade": rule["confidence"],
                        "lift": rule["lift"],
                        "baseado_em": rule["antecedent"]
                    }
                else:
                    # Actualizar se encontrar regra com maior confiança
                    if rule["confidence"] > recommendations[consequent]["probabilidade"]:
                        recommendations[consequent]["probabilidade"] = rule["confidence"]
                        recommendations[consequent]["lift"] = rule["lift"]
                        recommendations[consequent]["baseado_em"] = rule["antecedent"]
        
        # Ordenar por probabilidade
        sorted_recs = sorted(
            recommendations.values(),
            key=lambda x: x["probabilidade"],
            reverse=True
        )
        
        return sorted_recs[:max_recommendations]
    
    def get_summary(self) -> Dict:
        """Retorna resumo da análise."""
        if not self.rules:
            return {"error": "Nenhuma análise executada"}
        
        return {
            "total_regras": len(self.rules),
            "top_lift": self.rules[0] if self.rules else None,
            "lift_medio": sum(r["lift"] for r in self.rules) / len(self.rules),
            "confianca_media": sum(r["confidence"] for r in self.rules) / len(self.rules),
        }


def analyze_cross_sell(sales_df: pd.DataFrame, **kwargs) -> List[Dict]:
    """
    Função de conveniência para análise rápida de cross-sell.
    
    Args:
        sales_df: DataFrame com vendas
        **kwargs: Argumentos para AprioriAnalyzer
        
    Returns:
        Lista de regras de associação
    """
    analyzer = AprioriAnalyzer(**kwargs)
    return analyzer.analyze(sales_df)
