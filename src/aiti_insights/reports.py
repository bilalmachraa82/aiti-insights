"""
AITI Insights - Gerador de Relatórios
=====================================

Gera relatórios semanais em HTML/Markdown com oportunidades
identificadas e métricas de performance.
"""

import pandas as pd
from datetime import datetime
from typing import Optional, Dict, List
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


REPORT_TEMPLATE_HTML = """
<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AITI Insights - Relatório Semanal</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                line-height: 1.6; color: #333; max-width: 1200px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #1a73e8; margin-bottom: 10px; }}
        h2 {{ color: #5f6368; margin: 30px 0 15px; border-bottom: 2px solid #e8eaed; padding-bottom: 10px; }}
        h3 {{ color: #1a73e8; margin: 20px 0 10px; }}
        .header {{ text-align: center; margin-bottom: 40px; }}
        .subtitle {{ color: #5f6368; }}
        .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 30px 0; }}
        .metric {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; 
                   padding: 25px; border-radius: 12px; text-align: center; }}
        .metric-value {{ font-size: 2.5em; font-weight: bold; }}
        .metric-label {{ font-size: 0.9em; opacity: 0.9; margin-top: 5px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #e8eaed; }}
        th {{ background: #f8f9fa; font-weight: 600; color: #5f6368; }}
        tr:hover {{ background: #f8f9fa; }}
        .priority-alta {{ color: #d93025; font-weight: bold; }}
        .priority-media {{ color: #f9ab00; }}
        .priority-baixa {{ color: #188038; }}
        .action-box {{ background: #e8f5e9; border-left: 4px solid #34a853; padding: 15px; margin: 10px 0; border-radius: 4px; }}
        .footer {{ text-align: center; color: #5f6368; margin-top: 50px; padding-top: 20px; border-top: 1px solid #e8eaed; }}
        .segment-badge {{ display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.85em; font-weight: 500; }}
        .segment-Champions {{ background: #e8f5e9; color: #1b5e20; }}
        .segment-Loyal {{ background: #e3f2fd; color: #1565c0; }}
        .segment-AtRisk {{ background: #ffebee; color: #c62828; }}
        .segment-Hibernating {{ background: #f5f5f5; color: #616161; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 AITI Insights</h1>
        <p class="subtitle">Relatório de Oportunidades - Semana {week_number}</p>
        <p class="subtitle">{date_range}</p>
    </div>
    
    <div class="metrics">
        <div class="metric">
            <div class="metric-value">€{total_value:,.0f}</div>
            <div class="metric-label">Potencial Total</div>
        </div>
        <div class="metric" style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);">
            <div class="metric-value">{total_opportunities}</div>
            <div class="metric-label">Oportunidades</div>
        </div>
        <div class="metric" style="background: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%);">
            <div class="metric-value">{high_priority}</div>
            <div class="metric-label">Alta Prioridade</div>
        </div>
        <div class="metric" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
            <div class="metric-value">{total_customers}</div>
            <div class="metric-label">Clientes Impactados</div>
        </div>
    </div>
    
    <h2>🛒 Top Oportunidades Cross-Sell</h2>
    {cross_sell_table}
    
    <h2>🔄 Clientes para Reactivação</h2>
    {reactivation_table}
    
    <h2>⚠️ Clientes em Risco de Churn</h2>
    {churn_table}
    
    <h2>📊 Segmentação RFM</h2>
    {rfm_table}
    
    <h2>💡 Acções Recomendadas Esta Semana</h2>
    <div class="action-box">
        {actions}
    </div>
    
    <div class="footer">
        <p>Relatório gerado automaticamente por AITI Insights</p>
        <p>{generation_date}</p>
    </div>
</body>
</html>
"""


class ReportGenerator:
    """
    Gera relatórios em HTML e Markdown.
    
    Exemplo:
        generator = ReportGenerator()
        generator.generate_weekly_report(
            opportunities=opportunities,
            rfm_summary=rfm_summary,
            output_path="report.html"
        )
    """
    
    def __init__(self):
        self.report_data = {}
    
    def generate_weekly_report(
        self,
        opportunities: List[Dict],
        rfm_summary: pd.DataFrame = None,
        metrics: Dict = None,
        output_path: str = None,
        format: str = "html"
    ) -> str:
        """
        Gera relatório semanal.
        
        Args:
            opportunities: Lista de oportunidades
            rfm_summary: Resumo de segmentação RFM
            metrics: Métricas adicionais
            output_path: Caminho para guardar (opcional)
            format: Formato do output (html ou markdown)
            
        Returns:
            String com o relatório
        """
        # Separar oportunidades por tipo
        cross_sell = [op for op in opportunities if op["tipo"] == "cross_sell"]
        reactivation = [op for op in opportunities if op["tipo"] == "reactivation"]
        churn = [op for op in opportunities if op["tipo"] == "churn_risk"]
        
        # Calcular métricas
        total_value = sum(op.get("valor_estimado", 0) for op in opportunities)
        high_priority = len([op for op in opportunities if op.get("prioridade") == "alta"])
        unique_customers = len(set(op.get("cliente_id") for op in opportunities))
        
        # Gerar tabelas
        cross_sell_table = self._generate_table(
            cross_sell[:10],
            ["cliente_id", "produto_nome", "probabilidade", "valor_estimado", "prioridade"],
            ["Cliente", "Produto Sugerido", "Prob.", "Valor Est.", "Prioridade"]
        )
        
        reactivation_table = self._generate_table(
            reactivation[:10],
            ["cliente_nome", "segmento", "dias_sem_compra", "valor_historico", "valor_estimado"],
            ["Cliente", "Segmento", "Dias", "Valor Hist.", "Valor Est."]
        )
        
        churn_table = self._generate_table(
            churn[:10],
            ["cliente_nome", "dias_sem_compra", "valor_em_risco", "risco_score", "acao"],
            ["Cliente", "Dias", "Valor Risco", "Score", "Acção"]
        )
        
        # RFM Summary
        rfm_table = ""
        if rfm_summary is not None:
            rfm_table = rfm_summary.to_html(index=False, classes="rfm-table")
        
        # Gerar acções
        actions = self._generate_actions(opportunities)
        
        # Data
        now = datetime.now()
        week_number = now.isocalendar()[1]
        
        if format == "html":
            report = REPORT_TEMPLATE_HTML.format(
                week_number=week_number,
                date_range=f"{(now - pd.Timedelta(days=7)).strftime('%d/%m')} - {now.strftime('%d/%m/%Y')}",
                total_value=total_value,
                total_opportunities=len(opportunities),
                high_priority=high_priority,
                total_customers=unique_customers,
                cross_sell_table=cross_sell_table,
                reactivation_table=reactivation_table,
                churn_table=churn_table,
                rfm_table=rfm_table,
                actions=actions,
                generation_date=now.strftime("%d/%m/%Y %H:%M")
            )
        else:
            report = self._generate_markdown(
                opportunities, rfm_summary, total_value, high_priority, unique_customers
            )
        
        # Guardar se output_path especificado
        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(report)
            logger.info(f"Relatório guardado em {output_path}")
        
        return report
    
    def _generate_table(
        self,
        data: List[Dict],
        columns: List[str],
        headers: List[str]
    ) -> str:
        """Gera tabela HTML."""
        if not data:
            return "<p>Nenhuma oportunidade encontrada.</p>"
        
        rows = []
        for item in data:
            row_cells = []
            for col in columns:
                value = item.get(col, "-")
                
                # Formatação especial
                if col == "probabilidade":
                    value = f"{value*100:.0f}%"
                elif col in ["valor_estimado", "valor_historico", "valor_em_risco"]:
                    value = f"€{value:,.0f}"
                elif col == "prioridade":
                    value = f'<span class="priority-{value}">{value.upper()}</span>'
                elif col == "risco_score":
                    value = f"{value*100:.0f}%"
                
                row_cells.append(f"<td>{value}</td>")
            
            rows.append(f"<tr>{''.join(row_cells)}</tr>")
        
        header_row = "".join(f"<th>{h}</th>" for h in headers)
        
        return f"""
        <table>
            <thead><tr>{header_row}</tr></thead>
            <tbody>{''.join(rows)}</tbody>
        </table>
        """
    
    def _generate_actions(self, opportunities: List[Dict]) -> str:
        """Gera lista de acções recomendadas."""
        actions = []
        
        # Top 3 cross-sell
        cross_sell = sorted(
            [op for op in opportunities if op["tipo"] == "cross_sell"],
            key=lambda x: x.get("valor_estimado", 0),
            reverse=True
        )[:3]
        
        for op in cross_sell:
            actions.append(f"📞 Contactar <strong>{op['cliente_id']}</strong> para oferecer {op['produto_nome']} (€{op['valor_estimado']:,.0f} potencial)")
        
        # Reactivações urgentes
        reactivation = [op for op in opportunities if op["tipo"] == "reactivation" and op.get("prioridade") == "alta"][:2]
        for op in reactivation:
            actions.append(f"🔄 Campanha de reactivação para <strong>{op['cliente_nome']}</strong> ({op['dias_sem_compra']} dias)")
        
        # Churn risk
        churn = [op for op in opportunities if op["tipo"] == "churn_risk"][:2]
        for op in churn:
            actions.append(f"⚠️ Contacto urgente: <strong>{op['cliente_nome']}</strong> em risco de churn (€{op['valor_em_risco']:,.0f})")
        
        if not actions:
            return "<p>Sem acções urgentes esta semana.</p>"
        
        return "<ul>" + "".join(f"<li>{a}</li>" for a in actions) + "</ul>"
    
    def _generate_markdown(
        self,
        opportunities: List[Dict],
        rfm_summary: pd.DataFrame,
        total_value: float,
        high_priority: int,
        unique_customers: int
    ) -> str:
        """Gera relatório em Markdown."""
        now = datetime.now()
        
        md = f"""# 🎯 AITI Insights - Relatório Semanal

**Semana {now.isocalendar()[1]}** | Gerado em {now.strftime('%d/%m/%Y %H:%M')}

---

## 📊 Métricas

| Métrica | Valor |
|---------|-------|
| Potencial Total | €{total_value:,.0f} |
| Oportunidades | {len(opportunities)} |
| Alta Prioridade | {high_priority} |
| Clientes Impactados | {unique_customers} |

---

## 🛒 Top Oportunidades Cross-Sell

"""
        
        cross_sell = [op for op in opportunities if op["tipo"] == "cross_sell"][:5]
        for i, op in enumerate(cross_sell, 1):
            md += f"{i}. **{op['cliente_id']}** → {op['produto_nome']} ({op['probabilidade']*100:.0f}% prob, €{op['valor_estimado']:,.0f})\n"
        
        md += """
---

## 🔄 Clientes para Reactivação

"""
        
        reactivation = [op for op in opportunities if op["tipo"] == "reactivation"][:5]
        for i, op in enumerate(reactivation, 1):
            md += f"{i}. **{op['cliente_nome']}** - {op['dias_sem_compra']} dias sem compra (€{op['valor_historico']:,.0f} histórico)\n"
        
        md += f"""
---

*Relatório gerado automaticamente por AITI Insights*
"""
        
        return md
    
    def export_json(self, opportunities: List[Dict], output_path: str):
        """Exporta oportunidades em JSON."""
        data = {
            "generated_at": datetime.now().isoformat(),
            "total_opportunities": len(opportunities),
            "total_value": sum(op.get("valor_estimado", 0) for op in opportunities),
            "opportunities": opportunities
        }
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Dados exportados para {output_path}")


def generate_weekly_report(
    opportunities: List[Dict],
    rfm_summary: pd.DataFrame = None,
    output_path: str = None,
    **kwargs
) -> str:
    """Função de conveniência para gerar relatório."""
    generator = ReportGenerator()
    return generator.generate_weekly_report(
        opportunities=opportunities,
        rfm_summary=rfm_summary,
        output_path=output_path,
        **kwargs
    )
