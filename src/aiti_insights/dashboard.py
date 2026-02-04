"""
AITI Insights - Dashboard Streamlit
===================================

Interface web interactiva para visualização de oportunidades,
segmentação RFM e análise de vendas.

Executar: streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys
from datetime import datetime

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from aiti_insights.etl import ETLProcessor
from aiti_insights.apriori import AprioriAnalyzer
from aiti_insights.rfm import RFMAnalyzer, RFM_SEGMENTS
from aiti_insights.opportunities import OpportunityEngine
from aiti_insights.reports import ReportGenerator


# Configuração da página
st.set_page_config(
    page_title="AITI Insights",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a73e8;
        margin-bottom: 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)


def load_demo_data():
    """Carrega dados de demonstração."""
    data_dir = Path(__file__).parent.parent.parent.parent / "data" / "demo"
    
    if not data_dir.exists():
        st.error("Dados de demonstração não encontrados. Execute primeiro o script de setup.")
        st.stop()
    
    etl = ETLProcessor()
    
    sales_df = etl.load_sales(data_dir / "vendas.csv")
    customers_df = etl.load_customers(data_dir / "clientes.csv")
    products_df = etl.load_products(data_dir / "produtos.csv")
    
    return sales_df, customers_df, products_df, etl.get_summary()


def run_analysis(sales_df, customers_df, products_df):
    """Executa todas as análises."""
    # Apriori
    apriori = AprioriAnalyzer(min_support=0.02, min_confidence=0.3)
    rules = apriori.analyze(sales_df)
    
    # RFM
    rfm = RFMAnalyzer()
    rfm_df = rfm.analyze(sales_df)
    rfm_summary = rfm.get_segment_summary()
    rfm_insights = rfm.get_insights()
    
    # Oportunidades
    engine = OpportunityEngine(min_value=50)
    opportunities = engine.generate(
        sales_df=sales_df,
        rules=rules,
        rfm_segments=rfm_df,
        customers_df=customers_df,
        products_df=products_df
    )
    
    return {
        "rules": rules,
        "rfm_df": rfm_df,
        "rfm_summary": rfm_summary,
        "rfm_insights": rfm_insights,
        "opportunities": opportunities,
        "apriori_summary": apriori.get_summary()
    }


def main():
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown('<h1 class="main-header">🎯 AITI Insights</h1>', unsafe_allow_html=True)
        st.markdown("*Motor de Oportunidades Comerciais*")
    with col2:
        st.image("https://img.shields.io/badge/v1.0-MVP-blue", width=80)
    
    st.divider()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuração")
        
        data_source = st.radio(
            "Fonte de Dados",
            ["Demo (dados exemplo)", "Upload ficheiros"],
            index=0
        )
        
        if data_source == "Upload ficheiros":
            st.file_uploader("Vendas (CSV/Excel)", type=["csv", "xlsx"], key="sales_file")
            st.file_uploader("Clientes (opcional)", type=["csv", "xlsx"], key="customers_file")
            st.file_uploader("Produtos (opcional)", type=["csv", "xlsx"], key="products_file")
        
        st.divider()
        
        st.subheader("🔧 Parâmetros")
        min_support = st.slider("Suporte mínimo (Apriori)", 0.01, 0.20, 0.02, 0.01)
        min_confidence = st.slider("Confiança mínima", 0.2, 0.8, 0.3, 0.1)
        min_value = st.number_input("Valor mínimo oportunidade (€)", 0, 1000, 50, 50)
    
    # Carregar dados
    with st.spinner("Carregando dados..."):
        sales_df, customers_df, products_df, summary = load_demo_data()
    
    # Executar análises
    with st.spinner("Analisando dados..."):
        results = run_analysis(sales_df, customers_df, products_df)
    
    # Métricas principais
    opportunities = results["opportunities"]
    total_value = sum(op.get("valor_estimado", 0) for op in opportunities)
    high_priority = len([op for op in opportunities if op.get("prioridade") == "alta"])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "💰 Potencial Total",
            f"€{total_value:,.0f}",
            delta="+15% vs mês anterior"
        )
    
    with col2:
        st.metric(
            "🎯 Oportunidades",
            len(opportunities),
            delta=f"{high_priority} alta prioridade"
        )
    
    with col3:
        st.metric(
            "👥 Clientes Analisados",
            summary["clientes_unicos"],
            delta=f"{summary['transacoes']:,} transacções"
        )
    
    with col4:
        st.metric(
            "📦 Produtos",
            summary["produtos_unicos"],
            delta=f"{len(results['rules'])} regras"
        )
    
    st.divider()
    
    # Tabs principais
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🛒 Cross-Sell",
        "📊 Segmentação RFM",
        "🔄 Reactivação",
        "📈 Análise de Dados",
        "📋 Relatório"
    ])
    
    # Tab 1: Cross-Sell
    with tab1:
        st.header("Oportunidades de Cross-Sell")
        st.markdown("Produtos recomendados baseados em padrões de compra")
        
        cross_sell = [op for op in opportunities if op["tipo"] == "cross_sell"]
        
        if cross_sell:
            # Top oportunidades
            df_cross = pd.DataFrame(cross_sell[:20])
            df_cross["probabilidade"] = (df_cross["probabilidade"] * 100).round(0).astype(str) + "%"
            df_cross["valor_estimado"] = df_cross["valor_estimado"].apply(lambda x: f"€{x:,.0f}")
            
            st.dataframe(
                df_cross[["cliente_id", "produto_nome", "probabilidade", "valor_estimado", "prioridade"]],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "cliente_id": "Cliente",
                    "produto_nome": "Produto Sugerido",
                    "probabilidade": "Probabilidade",
                    "valor_estimado": "Valor Estimado",
                    "prioridade": st.column_config.TextColumn("Prioridade")
                }
            )
            
            # Regras de associação
            st.subheader("📊 Regras de Associação (Apriori)")
            
            rules_df = pd.DataFrame(results["rules"][:15])
            if not rules_df.empty:
                rules_df["antecedent"] = rules_df["antecedent"].apply(lambda x: ", ".join(x))
                rules_df["consequent"] = rules_df["consequent"].apply(lambda x: ", ".join(x))
                rules_df["confidence"] = (rules_df["confidence"] * 100).round(0).astype(str) + "%"
                
                st.dataframe(
                    rules_df[["antecedent", "consequent", "confidence", "lift", "count"]],
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "antecedent": "Se compra...",
                        "consequent": "Provavelmente compra...",
                        "confidence": "Confiança",
                        "lift": "Lift",
                        "count": "Ocorrências"
                    }
                )
        else:
            st.info("Nenhuma oportunidade de cross-sell identificada com os parâmetros actuais.")
    
    # Tab 2: RFM
    with tab2:
        st.header("Segmentação RFM")
        st.markdown("Classificação de clientes por Recência, Frequência e Valor")
        
        rfm_summary = results["rfm_summary"]
        rfm_insights = results["rfm_insights"]
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de segmentos
            fig = px.pie(
                rfm_summary,
                values="count",
                names="segment",
                title="Distribuição de Clientes por Segmento",
                color="segment",
                color_discrete_map={
                    "Champions": "#2E7D32",
                    "Loyal": "#4CAF50",
                    "At Risk": "#F44336",
                    "Hibernating": "#9E9E9E",
                    "Need Attention": "#FFC107",
                    "Potential Loyalist": "#8BC34A",
                    "New Customers": "#03A9F4",
                    "Promising": "#00BCD4",
                    "About to Sleep": "#FF9800",
                    "Lost": "#607D8B"
                }
            )
            fig.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Tabela de segmentos
            st.dataframe(
                rfm_summary[["segment", "count", "percentage", "avg_monetary", "total_monetary"]],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "segment": "Segmento",
                    "count": "Clientes",
                    "percentage": st.column_config.NumberColumn("% do Total", format="%.1f%%"),
                    "avg_monetary": st.column_config.NumberColumn("Valor Médio", format="€%.0f"),
                    "total_monetary": st.column_config.NumberColumn("Valor Total", format="€%.0f")
                }
            )
        
        # Insights
        st.subheader("💡 Insights")
        for insight in rfm_insights["insights"]:
            st.markdown(f"• {insight}")
    
    # Tab 3: Reactivação
    with tab3:
        st.header("Clientes para Reactivação")
        st.markdown("Clientes dormentes ou em risco que precisam de atenção")
        
        reactivation = [op for op in opportunities if op["tipo"] in ["reactivation", "churn_risk"]]
        
        if reactivation:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                df_react = pd.DataFrame(reactivation[:20])
                df_react["valor_estimado"] = df_react["valor_estimado"].apply(lambda x: f"€{x:,.0f}")
                
                st.dataframe(
                    df_react[["cliente_nome", "tipo", "segmento", "dias_sem_compra", "valor_estimado", "acao"]],
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "cliente_nome": "Cliente",
                        "tipo": "Tipo",
                        "segmento": "Segmento",
                        "dias_sem_compra": "Dias sem Compra",
                        "valor_estimado": "Valor Recuperável",
                        "acao": "Acção Recomendada"
                    }
                )
            
            with col2:
                # Resumo por tipo
                by_type = pd.DataFrame(reactivation).groupby("tipo").agg({
                    "cliente_id": "count",
                    "valor_estimado": "sum"
                }).reset_index()
                by_type.columns = ["Tipo", "Clientes", "Valor"]
                
                fig = px.bar(
                    by_type,
                    x="Tipo",
                    y="Valor",
                    title="Valor por Tipo de Oportunidade",
                    color="Tipo"
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhum cliente identificado para reactivação.")
    
    # Tab 4: Análise de Dados
    with tab4:
        st.header("Análise de Dados")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Vendas ao longo do tempo
            sales_by_month = sales_df.groupby(sales_df["data"].dt.to_period("M")).agg({
                "valor": "sum",
                "cliente_id": "nunique"
            }).reset_index()
            sales_by_month["data"] = sales_by_month["data"].astype(str)
            
            fig = px.line(
                sales_by_month,
                x="data",
                y="valor",
                title="Vendas Mensais",
                markers=True
            )
            fig.update_layout(xaxis_title="Mês", yaxis_title="Valor (€)")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Top produtos
            top_products = sales_df.groupby("produto_id")["valor"].sum().nlargest(10).reset_index()
            
            # Merge com nomes se disponível
            if products_df is not None and "nome" in products_df.columns:
                top_products = top_products.merge(
                    products_df[["produto_id", "nome"]],
                    on="produto_id",
                    how="left"
                )
                top_products["produto"] = top_products["nome"].fillna(top_products["produto_id"])
            else:
                top_products["produto"] = top_products["produto_id"]
            
            fig = px.bar(
                top_products,
                x="valor",
                y="produto",
                orientation="h",
                title="Top 10 Produtos por Valor"
            )
            fig.update_layout(yaxis=dict(categoryorder="total ascending"))
            st.plotly_chart(fig, use_container_width=True)
        
        # Resumo dos dados
        st.subheader("📋 Resumo dos Dados")
        
        cols = st.columns(4)
        cols[0].metric("Período", f"{summary['periodo']['dias']} dias")
        cols[1].metric("Total Transacções", f"{summary['transacoes']:,}")
        cols[2].metric("Valor Total", f"€{summary['valor_total']:,.0f}")
        cols[3].metric("Ticket Médio", f"€{summary['ticket_medio']:,.0f}")
    
    # Tab 5: Relatório
    with tab5:
        st.header("Gerar Relatório Semanal")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            report_format = st.radio("Formato", ["HTML", "Markdown"], horizontal=True)
            
            if st.button("📄 Gerar Relatório", type="primary"):
                generator = ReportGenerator()
                report = generator.generate_weekly_report(
                    opportunities=opportunities,
                    rfm_summary=rfm_summary,
                    format=report_format.lower()
                )
                
                st.success("Relatório gerado com sucesso!")
                
                # Download button
                st.download_button(
                    label="⬇️ Download Relatório",
                    data=report,
                    file_name=f"aiti_insights_report_{datetime.now().strftime('%Y%m%d')}.{'html' if report_format == 'HTML' else 'md'}",
                    mime="text/html" if report_format == "HTML" else "text/markdown"
                )
                
                # Preview
                if report_format == "HTML":
                    st.components.v1.html(report, height=800, scrolling=True)
                else:
                    st.markdown(report)
        
        with col2:
            st.info("""
            **O relatório inclui:**
            - Métricas principais
            - Top oportunidades cross-sell
            - Clientes para reactivação
            - Análise de churn risk
            - Segmentação RFM
            - Acções recomendadas
            """)
    
    # Footer
    st.divider()
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "AITI Insights v1.0 | Desenvolvido por AiParaTi | "
        f"Dados actualizados: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
