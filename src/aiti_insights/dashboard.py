"""
AITI Insights - Premium Dashboard
==================================
Motor de Oportunidades Comerciais - Interface Premium
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import sys
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from aiti_insights.etl import ETLProcessor
from aiti_insights.apriori import AprioriAnalyzer
from aiti_insights.rfm import RFMAnalyzer, RFM_SEGMENTS
from aiti_insights.opportunities import OpportunityEngine
from aiti_insights.reports import ReportGenerator

# === PAGE CONFIG ===
st.set_page_config(
    page_title="AITI Insights | Motor de Oportunidades",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === PREMIUM CSS ===
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* Global */
    .stApp { background: #F8FAFC; }
    .main .block-container { padding-top: 1rem; max-width: 1400px; }
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* Hide default streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Premium Header */
    .premium-header {
        background: linear-gradient(135deg, #1E3A5F 0%, #1E40AF 50%, #3B82F6 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 10px 40px rgba(30, 64, 175, 0.3);
    }
    .premium-header-left { display: flex; align-items: center; gap: 1rem; }
    .premium-logo {
        width: 56px; height: 56px;
        background: rgba(255,255,255,0.15);
        border-radius: 14px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.8rem;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
    }
    .premium-title { color: white; font-size: 1.8rem; font-weight: 700; margin: 0; letter-spacing: -0.02em; }
    .premium-subtitle { color: rgba(255,255,255,0.8); font-size: 0.95rem; font-weight: 400; margin: 0; }
    .premium-badge {
        background: rgba(255,255,255,0.15);
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        border: 1px solid rgba(255,255,255,0.2);
    }

    /* KPI Cards */
    .kpi-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.08);
    }
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
        border-radius: 16px 16px 0 0;
    }
    .kpi-blue::before { background: linear-gradient(90deg, #1E40AF, #3B82F6); }
    .kpi-green::before { background: linear-gradient(90deg, #059669, #10B981); }
    .kpi-amber::before { background: linear-gradient(90deg, #D97706, #F59E0B); }
    .kpi-purple::before { background: linear-gradient(90deg, #7C3AED, #A78BFA); }
    .kpi-icon {
        width: 48px; height: 48px;
        border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.4rem;
        margin-bottom: 0.75rem;
    }
    .kpi-icon-blue { background: #EFF6FF; }
    .kpi-icon-green { background: #ECFDF5; }
    .kpi-icon-amber { background: #FFFBEB; }
    .kpi-icon-purple { background: #F5F3FF; }
    .kpi-label { color: #64748B; font-size: 0.8rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.25rem; }
    .kpi-value { color: #1E293B; font-size: 1.8rem; font-weight: 700; line-height: 1.2; }
    .kpi-delta { font-size: 0.8rem; font-weight: 500; margin-top: 0.35rem; }
    .kpi-delta-up { color: #059669; }
    .kpi-delta-neutral { color: #64748B; }

    /* Section Headers */
    .section-header {
        display: flex; align-items: center; gap: 0.75rem;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid #E2E8F0;
    }
    .section-icon {
        width: 40px; height: 40px;
        background: #EFF6FF;
        border-radius: 10px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.2rem;
    }
    .section-title { font-size: 1.3rem; font-weight: 700; color: #1E293B; margin: 0; }
    .section-desc { font-size: 0.85rem; color: #64748B; margin: 0; }

    /* Cards */
    .insight-card {
        background: white;
        border-radius: 12px;
        padding: 1.25rem;
        border: 1px solid #E2E8F0;
        margin-bottom: 0.75rem;
    }
    .insight-card-highlight {
        background: linear-gradient(135deg, #EFF6FF 0%, #F0F9FF 100%);
        border: 1px solid #BFDBFE;
    }

    /* Sidebar Premium */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1E293B 0%, #0F172A 100%);
    }
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3,
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown label,
    section[data-testid="stSidebar"] .stMarkdown span,
    section[data-testid="stSidebar"] .stMarkdown li {
        color: #E2E8F0 !important;
    }
    section[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.1); }

    /* Nav pills */
    .nav-pill {
        display: flex; align-items: center; gap: 0.5rem;
        padding: 0.6rem 1rem;
        border-radius: 8px;
        color: #94A3B8;
        font-size: 0.9rem;
        font-weight: 500;
        margin-bottom: 0.25rem;
        cursor: pointer;
        transition: all 0.2s;
    }
    .nav-pill:hover { background: rgba(255,255,255,0.05); color: white; }
    .nav-pill-active { background: rgba(59,130,246,0.2); color: #60A5FA; border: 1px solid rgba(59,130,246,0.3); }

    /* Info box */
    .info-box {
        background: linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%);
        border-radius: 12px;
        padding: 1.25rem;
        color: white;
        margin: 1rem 0;
    }
    .info-box h4 { color: white; margin: 0 0 0.5rem 0; font-size: 0.95rem; }
    .info-box p { color: rgba(255,255,255,0.85); margin: 0; font-size: 0.85rem; line-height: 1.5; }

    /* Table styling */
    .stDataFrame { border-radius: 12px; overflow: hidden; }

    /* Plotly charts */
    .stPlotlyChart { border-radius: 12px; background: white; padding: 0.5rem; border: 1px solid #E2E8F0; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background: white;
        border-radius: 12px;
        padding: 0.25rem;
        border: 1px solid #E2E8F0;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.5rem 1.25rem;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background: #1E40AF !important;
        color: white !important;
    }

    /* Welcome box */
    .welcome-box {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
    }
    .welcome-box h3 { color: #1E293B; margin-bottom: 0.5rem; }
    .welcome-box p { color: #64748B; }

    /* Footer */
    .premium-footer {
        text-align: center;
        padding: 1.5rem;
        color: #94A3B8;
        font-size: 0.8rem;
        border-top: 1px solid #E2E8F0;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)


# === PLOTLY THEME ===
COLORS = {
    "primary": "#1E40AF",
    "primary_light": "#3B82F6",
    "secondary": "#10B981",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "purple": "#7C3AED",
    "slate": "#64748B",
    "dark": "#1E293B",
}

CHART_COLORS = ["#1E40AF", "#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#7C3AED", "#06B6D4", "#EC4899", "#8B5CF6", "#14B8A6"]

PLOTLY_LAYOUT = dict(
    font=dict(family="Inter, sans-serif", color="#1E293B"),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=20, r=20, t=50, b=20),
    title_font=dict(size=16, color="#1E293B"),
    hoverlabel=dict(bgcolor="white", font_size=13, font_family="Inter"),
)


def load_demo_data():
    """Carrega dados de demonstração."""
    data_dir = Path(__file__).parent.parent.parent / "data" / "demo"

    if not data_dir.exists():
        st.error("⚠️ Dados de demonstração não encontrados.")
        st.stop()

    etl = ETLProcessor()
    sales_df = etl.load_sales(data_dir / "vendas.csv")
    customers_df = etl.load_customers(data_dir / "clientes.csv")
    products_df = etl.load_products(data_dir / "produtos.csv")

    # Ensure consistent key types
    sales_df["cliente_id"] = sales_df["cliente_id"].astype(str)
    sales_df["produto_id"] = sales_df["produto_id"].astype(str)
    if customers_df is not None and "cliente_id" in customers_df.columns:
        customers_df["cliente_id"] = customers_df["cliente_id"].astype(str)
    if products_df is not None and "produto_id" in products_df.columns:
        products_df["produto_id"] = products_df["produto_id"].astype(str)

    # Enrich sales with customer/product names
    if customers_df is not None and "nome" in customers_df.columns:
        sales_df = sales_df.merge(
            customers_df[["cliente_id", "nome"]].rename(columns={"nome": "cliente_nome"}),
            on="cliente_id", how="left"
        )
    if products_df is not None:
        merge_cols = ["produto_id"]
        rename = {}
        if "nome" in products_df.columns:
            merge_cols.append("nome")
            rename["nome"] = "produto_nome"
        if "categoria" in products_df.columns:
            merge_cols.append("categoria")
        prod_merge = products_df[merge_cols].drop_duplicates(subset=["produto_id"])
        if rename:
            prod_merge = prod_merge.rename(columns=rename)
        sales_df = sales_df.merge(prod_merge, on="produto_id", how="left")

    # Add synthetic payment status if missing
    if "estado_pagamento" not in sales_df.columns:
        import numpy as np
        np.random.seed(42)
        sales_df["estado_pagamento"] = np.random.choice(
            ["Pago", "Pendente", "Vencido"], len(sales_df), p=[0.6, 0.25, 0.15]
        )

    return sales_df, customers_df, products_df, etl.get_summary()


def run_analysis(sales_df, customers_df, products_df, min_support=0.02, min_confidence=0.3, min_value=50):
    """Executa todas as análises."""
    apriori = AprioriAnalyzer(min_support=min_support, min_confidence=min_confidence)
    rules = apriori.analyze(sales_df)

    rfm = RFMAnalyzer()
    rfm_df = rfm.analyze(sales_df)
    rfm_summary = rfm.get_segment_summary()
    rfm_insights = rfm.get_insights()

    engine = OpportunityEngine(min_value=min_value)
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
        "apriori_summary": apriori.get_summary(),
        "sales_df": sales_df,
        "customers_df": customers_df,
        "products_df": products_df,
    }


def render_header():
    """Premium header."""
    st.markdown("""
    <div class="premium-header">
        <div class="premium-header-left">
            <div class="premium-logo">🎯</div>
            <div>
                <h1 class="premium-title">AITI Insights</h1>
                <p class="premium-subtitle">Motor de Oportunidades Comerciais</p>
            </div>
        </div>
        <div class="premium-badge">✨ Premium Analytics</div>
    </div>
    """, unsafe_allow_html=True)


def render_kpi_cards(summary, opportunities, rules):
    """KPI cards premium."""
    total_value = sum(op.get("valor_estimado", 0) for op in opportunities)
    high_priority = len([op for op in opportunities if op.get("prioridade") == "alta"])

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="kpi-card kpi-blue">
            <div class="kpi-icon kpi-icon-blue">💰</div>
            <div class="kpi-label">Potencial Comercial</div>
            <div class="kpi-value">€{total_value:,.0f}</div>
            <div class="kpi-delta kpi-delta-up">↗ Oportunidades identificadas por IA</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="kpi-card kpi-green">
            <div class="kpi-icon kpi-icon-green">🎯</div>
            <div class="kpi-label">Oportunidades</div>
            <div class="kpi-value">{len(opportunities)}</div>
            <div class="kpi-delta kpi-delta-up">🔴 {high_priority} alta prioridade</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="kpi-card kpi-amber">
            <div class="kpi-icon kpi-icon-amber">👥</div>
            <div class="kpi-label">Clientes Analisados</div>
            <div class="kpi-value">{summary['clientes_unicos']}</div>
            <div class="kpi-delta kpi-delta-neutral">📊 {summary['transacoes']:,} transacções processadas</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="kpi-card kpi-purple">
            <div class="kpi-icon kpi-icon-purple">🧠</div>
            <div class="kpi-label">Regras de IA</div>
            <div class="kpi-value">{len(rules)}</div>
            <div class="kpi-delta kpi-delta-neutral">📦 {summary['produtos_unicos']} produtos mapeados</div>
        </div>
        """, unsafe_allow_html=True)


def render_sidebar(summary):
    """Premium sidebar."""
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🎯</div>
            <h2 style="margin: 0; font-size: 1.2rem;">AITI Insights</h2>
            <p style="margin: 0; font-size: 0.8rem; opacity: 0.7;">by AiParaTi</p>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        # How to use
        st.markdown("### 📖 Como Usar")
        st.markdown("""
        1. **📊 Visão Geral** — KPIs e métricas
        2. **🛒 Cross-Sell** — Sugestões de venda cruzada
        3. **👥 Segmentação** — Perfis RFM de clientes
        4. **🔄 Reactivação** — Clientes dormentes
        5. **📈 Análise** — Tendências e padrões
        6. **📋 Relatório** — Export PDF/HTML
        """)

        st.divider()

        st.markdown("### ⚙️ Configuração")

        data_source = st.radio(
            "Fonte de Dados",
            ["📦 Demo (pré-carregado)", "📁 Upload ficheiros"],
            index=0
        )

        if "Upload" in data_source:
            st.file_uploader("Vendas (CSV/Excel)", type=["csv", "xlsx"], key="sales_file")
            st.file_uploader("Clientes (opcional)", type=["csv", "xlsx"], key="customers_file")
            st.file_uploader("Produtos (opcional)", type=["csv", "xlsx"], key="products_file")

        st.divider()

        st.markdown("### 🔧 Parâmetros da IA")
        min_support = st.slider("Suporte mínimo", 0.01, 0.20, 0.02, 0.01,
                                help="Frequência mínima para padrões de compra")
        min_confidence = st.slider("Confiança mínima", 0.2, 0.8, 0.3, 0.1,
                                   help="Grau de certeza das recomendações")
        min_value = st.number_input("Valor mínimo (€)", 0, 1000, 50, 50,
                                    help="Valor mínimo para considerar oportunidade")

        st.divider()

        # Info box
        st.markdown("""
        <div class="info-box">
            <h4>💡 Dica</h4>
            <p>Os dados demo incluem vendas reais anonimizadas. 
            Faça upload dos seus próprios ficheiros para análise personalizada.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="text-align: center; padding: 1rem 0; font-size: 0.75rem; opacity: 0.5;">
            Última actualização: {datetime.now().strftime('%d/%m/%Y %H:%M')}<br>
            v2.0 Premium
        </div>
        """, unsafe_allow_html=True)

        return min_support, min_confidence, min_value


def render_overview(summary, results):
    """Overview section with charts."""
    sales_df = results["sales_df"]

    st.markdown("""
    <div class="section-header">
        <div class="section-icon">📊</div>
        <div>
            <h2 class="section-title">Visão Geral do Negócio</h2>
            <p class="section-desc">Análise completa dos dados comerciais</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        # Revenue trend
        sales_by_month = sales_df.groupby(sales_df["data"].dt.to_period("M")).agg({
            "valor": "sum",
            "cliente_id": "nunique"
        }).reset_index()
        sales_by_month["data"] = sales_by_month["data"].astype(str)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=sales_by_month["data"],
            y=sales_by_month["valor"],
            mode="lines+markers",
            name="Receita",
            line=dict(color=COLORS["primary"], width=3),
            marker=dict(size=8, color=COLORS["primary"]),
            fill="tozeroy",
            fillcolor="rgba(30, 64, 175, 0.08)",
        ))
        fig.update_layout(
            title="📈 Evolução da Receita Mensal",
            xaxis_title="",
            yaxis_title="Receita (€)",
            yaxis=dict(gridcolor="#F1F5F9", tickprefix="€", tickformat=","),
            xaxis=dict(gridcolor="#F1F5F9"),
            **PLOTLY_LAYOUT
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Category breakdown
        cat_data = sales_df.groupby("categoria")["valor"].sum().reset_index()
        cat_data = cat_data.sort_values("valor", ascending=False)

        fig = go.Figure(data=[go.Pie(
            labels=cat_data["categoria"],
            values=cat_data["valor"],
            hole=0.55,
            marker=dict(colors=CHART_COLORS),
            textinfo="label+percent",
            textposition="outside",
            textfont=dict(size=12),
        )])
        fig.update_layout(
            title="🏷️ Receita por Categoria",
            showlegend=False,
            **PLOTLY_LAYOUT,
            annotations=[dict(
                text=f"€{cat_data['valor'].sum():,.0f}",
                x=0.5, y=0.5, font_size=18, font_color=COLORS["dark"],
                showarrow=False, font_weight=700
            )]
        )
        st.plotly_chart(fig, use_container_width=True)

    # Second row
    col1, col2 = st.columns(2)

    with col1:
        # Payment status
        payment_data = sales_df.groupby("estado_pagamento")["valor"].sum().reset_index()
        color_map = {"Pago": "#10B981", "Pendente": "#F59E0B", "Vencido": "#EF4444"}

        fig = go.Figure(data=[go.Bar(
            x=payment_data["estado_pagamento"],
            y=payment_data["valor"],
            marker_color=[color_map.get(s, "#94A3B8") for s in payment_data["estado_pagamento"]],
            text=[f"€{v:,.0f}" for v in payment_data["valor"]],
            textposition="outside",
            textfont=dict(size=12, color=COLORS["dark"]),
        )])
        fig.update_layout(
            title="💳 Estado dos Pagamentos",
            xaxis_title="",
            yaxis_title="Valor (€)",
            yaxis=dict(gridcolor="#F1F5F9", tickprefix="€"),
            showlegend=False,
            **PLOTLY_LAYOUT
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Top clients
        top_clients = sales_df.groupby("cliente_nome")["valor"].sum().nlargest(8).reset_index()
        top_clients = top_clients.sort_values("valor", ascending=True)

        fig = go.Figure(data=[go.Bar(
            y=top_clients["cliente_nome"].str[:30],
            x=top_clients["valor"],
            orientation="h",
            marker=dict(
                color=top_clients["valor"],
                colorscale=[[0, "#93C5FD"], [1, "#1E40AF"]],
            ),
            text=[f"€{v:,.0f}" for v in top_clients["valor"]],
            textposition="outside",
            textfont=dict(size=11),
        )])
        fig.update_layout(
            title="🏆 Top 8 Clientes por Valor",
            xaxis_title="",
            yaxis_title="",
            xaxis=dict(gridcolor="#F1F5F9", tickprefix="€"),
            **PLOTLY_LAYOUT,
            margin=dict(l=200, r=60, t=50, b=20),
        )
        st.plotly_chart(fig, use_container_width=True)


def render_cross_sell(results):
    """Cross-sell opportunities."""
    st.markdown("""
    <div class="section-header">
        <div class="section-icon">🛒</div>
        <div>
            <h2 class="section-title">Oportunidades de Cross-Sell</h2>
            <p class="section-desc">Produtos recomendados pela IA baseados em padrões de compra</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    opportunities = results["opportunities"]
    cross_sell = [op for op in opportunities if op["tipo"] == "cross_sell"]

    if not cross_sell:
        st.info("🔍 Nenhuma oportunidade de cross-sell com os parâmetros actuais. Tente reduzir o suporte mínimo.")
        return

    # Summary metrics
    total_val = sum(op.get("valor_estimado", 0) for op in cross_sell)
    avg_prob = sum(op.get("probabilidade", 0) for op in cross_sell) / len(cross_sell) * 100

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Oportunidades", len(cross_sell))
    c2.metric("Valor Potencial", f"€{total_val:,.0f}")
    c3.metric("Confiança Média", f"{avg_prob:.0f}%")

    st.markdown("")

    col1, col2 = st.columns([3, 2])

    with col1:
        df_cross = pd.DataFrame(cross_sell[:20])
        if "probabilidade" in df_cross.columns:
            df_cross["prob_pct"] = (df_cross["probabilidade"] * 100).round(0)
        if "valor_estimado" in df_cross.columns:
            df_cross["valor_fmt"] = df_cross["valor_estimado"].apply(lambda x: f"€{x:,.0f}")

        display_cols = []
        col_config = {}

        if "cliente_nome" in df_cross.columns:
            display_cols.append("cliente_nome")
            col_config["cliente_nome"] = st.column_config.TextColumn("👤 Cliente")
        elif "cliente_id" in df_cross.columns:
            display_cols.append("cliente_id")
            col_config["cliente_id"] = "👤 Cliente"

        if "produto_nome" in df_cross.columns:
            display_cols.append("produto_nome")
            col_config["produto_nome"] = st.column_config.TextColumn("📦 Produto Sugerido")

        if "prob_pct" in df_cross.columns:
            display_cols.append("prob_pct")
            col_config["prob_pct"] = st.column_config.ProgressColumn("🎯 Confiança", min_value=0, max_value=100, format="%d%%")

        if "valor_fmt" in df_cross.columns:
            display_cols.append("valor_fmt")
            col_config["valor_fmt"] = st.column_config.TextColumn("💰 Valor Est.")

        if "prioridade" in df_cross.columns:
            display_cols.append("prioridade")
            col_config["prioridade"] = st.column_config.TextColumn("⚡ Prioridade")

        if display_cols:
            st.dataframe(df_cross[display_cols], use_container_width=True, hide_index=True, column_config=col_config)

    with col2:
        # Association rules visualization
        rules = results["rules"]
        if rules:
            rules_df = pd.DataFrame(rules[:10])
            if not rules_df.empty and "confidence" in rules_df.columns and "lift" in rules_df.columns:
                fig = go.Figure(data=[go.Scatter(
                    x=rules_df["confidence"],
                    y=rules_df["lift"],
                    mode="markers",
                    marker=dict(
                        size=rules_df.get("count", [10]*len(rules_df)),
                        sizemode="area",
                        sizeref=max(rules_df.get("count", [10])) / 500 if "count" in rules_df.columns else 1,
                        sizemin=8,
                        color=rules_df["confidence"],
                        colorscale=[[0, "#93C5FD"], [1, "#1E40AF"]],
                        showscale=True,
                        colorbar=dict(title="Confiança"),
                    ),
                    text=[f"{', '.join(r.get('antecedent', []))} → {', '.join(r.get('consequent', []))}" for r in rules[:10]],
                    hovertemplate="<b>%{text}</b><br>Confiança: %{x:.0%}<br>Lift: %{y:.1f}<extra></extra>",
                )])
                fig.update_layout(
                    title="🔗 Regras de Associação",
                    xaxis_title="Confiança",
                    yaxis_title="Lift",
                    xaxis=dict(gridcolor="#F1F5F9", tickformat=".0%"),
                    yaxis=dict(gridcolor="#F1F5F9"),
                    **PLOTLY_LAYOUT
                )
                st.plotly_chart(fig, use_container_width=True)


def render_rfm(results):
    """RFM Segmentation."""
    st.markdown("""
    <div class="section-header">
        <div class="section-icon">👥</div>
        <div>
            <h2 class="section-title">Segmentação de Clientes (RFM)</h2>
            <p class="section-desc">Classificação por Recência, Frequência e Valor Monetário</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    rfm_summary = results["rfm_summary"]
    rfm_insights = results["rfm_insights"]

    # Infographic explanation
    st.markdown("""
    <div class="insight-card insight-card-highlight">
        <div style="display: flex; gap: 2rem; align-items: center; flex-wrap: wrap;">
            <div style="flex: 1; min-width: 200px; text-align: center;">
                <div style="font-size: 2rem;">⏰</div>
                <div style="font-weight: 600; color: #1E40AF;">Recência</div>
                <div style="font-size: 0.85rem; color: #64748B;">Quando foi a última compra?</div>
            </div>
            <div style="flex: 1; min-width: 200px; text-align: center;">
                <div style="font-size: 2rem;">🔄</div>
                <div style="font-weight: 600; color: #10B981;">Frequência</div>
                <div style="font-size: 0.85rem; color: #64748B;">Quantas vezes compra?</div>
            </div>
            <div style="flex: 1; min-width: 200px; text-align: center;">
                <div style="font-size: 2rem;">💎</div>
                <div style="font-weight: 600; color: #F59E0B;">Monetário</div>
                <div style="font-size: 0.85rem; color: #64748B;">Quanto gasta em média?</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        # Treemap
        if not rfm_summary.empty and "segment" in rfm_summary.columns:
            segment_colors = {
                "Champions": "#059669", "Loyal": "#10B981", "Potential Loyalist": "#34D399",
                "New Customers": "#3B82F6", "Promising": "#06B6D4",
                "Need Attention": "#F59E0B", "About to Sleep": "#FB923C",
                "At Risk": "#EF4444", "Hibernating": "#94A3B8", "Lost": "#475569"
            }

            fig = go.Figure(data=[go.Treemap(
                labels=rfm_summary["segment"],
                parents=[""] * len(rfm_summary),
                values=rfm_summary["count"],
                text=[f"{row['count']} clientes<br>€{row.get('total_monetary', 0):,.0f}" for _, row in rfm_summary.iterrows()],
                textinfo="label+text",
                marker=dict(colors=[segment_colors.get(s, "#94A3B8") for s in rfm_summary["segment"]]),
                hovertemplate="<b>%{label}</b><br>%{text}<extra></extra>",
            )])
            fig.update_layout(title="🗺️ Mapa de Segmentos", **PLOTLY_LAYOUT)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Bar chart by value
        if not rfm_summary.empty:
            sorted_rfm = rfm_summary.sort_values("total_monetary" if "total_monetary" in rfm_summary.columns else "count", ascending=True)

            fig = go.Figure(data=[go.Bar(
                y=sorted_rfm["segment"],
                x=sorted_rfm.get("total_monetary", sorted_rfm["count"]),
                orientation="h",
                marker=dict(
                    color=[segment_colors.get(s, "#94A3B8") for s in sorted_rfm["segment"]],
                ),
                text=[f"€{v:,.0f}" for v in sorted_rfm.get("total_monetary", sorted_rfm["count"])],
                textposition="outside",
                textfont=dict(size=11),
            )])
            fig.update_layout(
                title="💰 Valor por Segmento",
                xaxis=dict(gridcolor="#F1F5F9", tickprefix="€"),
                **PLOTLY_LAYOUT,
                margin=dict(l=150, r=60, t=50, b=20),
            )
            st.plotly_chart(fig, use_container_width=True)

    # Segment table
    st.markdown("#### 📋 Detalhe por Segmento")
    if not rfm_summary.empty:
        display_rfm = rfm_summary.copy()
        col_config_rfm = {
            "segment": st.column_config.TextColumn("Segmento"),
            "count": st.column_config.NumberColumn("Clientes"),
        }
        cols_to_show = ["segment", "count"]
        if "percentage" in display_rfm.columns:
            cols_to_show.append("percentage")
            col_config_rfm["percentage"] = st.column_config.NumberColumn("% Total", format="%.1f%%")
        if "avg_monetary" in display_rfm.columns:
            cols_to_show.append("avg_monetary")
            col_config_rfm["avg_monetary"] = st.column_config.NumberColumn("Valor Médio", format="€%.0f")
        if "total_monetary" in display_rfm.columns:
            cols_to_show.append("total_monetary")
            col_config_rfm["total_monetary"] = st.column_config.NumberColumn("Valor Total", format="€%.0f")

        st.dataframe(display_rfm[cols_to_show], use_container_width=True, hide_index=True, column_config=col_config_rfm)

    # Insights
    if rfm_insights and "insights" in rfm_insights:
        st.markdown("#### 💡 Insights da IA")
        for i, insight in enumerate(rfm_insights["insights"][:5]):
            st.markdown(f"""
            <div class="insight-card">
                <span style="color: #1E40AF; font-weight: 600;">Insight #{i+1}:</span> {insight}
            </div>
            """, unsafe_allow_html=True)


def render_reactivation(results):
    """Reactivation tab."""
    st.markdown("""
    <div class="section-header">
        <div class="section-icon">🔄</div>
        <div>
            <h2 class="section-title">Clientes para Reactivação</h2>
            <p class="section-desc">Clientes dormentes com alto potencial de recuperação</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    opportunities = results["opportunities"]
    reactivation = [op for op in opportunities if op["tipo"] in ["reactivation", "churn_risk"]]

    if not reactivation:
        st.info("✅ Nenhum cliente em risco de churn identificado!")
        return

    # Metrics
    total_val = sum(op.get("valor_estimado", 0) for op in reactivation)
    churn = [op for op in reactivation if op["tipo"] == "churn_risk"]
    dormant = [op for op in reactivation if op["tipo"] == "reactivation"]

    c1, c2, c3 = st.columns(3)
    c1.metric("💰 Valor Recuperável", f"€{total_val:,.0f}")
    c2.metric("⚠️ Risco de Churn", len(churn))
    c3.metric("😴 Dormentes", len(dormant))

    col1, col2 = st.columns([3, 2])

    with col1:
        df_react = pd.DataFrame(reactivation[:20])
        display_cols = []
        col_config = {}

        for col_name, label in [("cliente_nome", "👤 Cliente"), ("tipo", "📌 Tipo"),
                                 ("segmento", "🏷️ Segmento"), ("dias_sem_compra", "📅 Dias s/ Compra")]:
            if col_name in df_react.columns:
                display_cols.append(col_name)
                col_config[col_name] = label

        if "valor_estimado" in df_react.columns:
            df_react["valor_fmt"] = df_react["valor_estimado"].apply(lambda x: f"€{x:,.0f}")
            display_cols.append("valor_fmt")
            col_config["valor_fmt"] = "💰 Valor"

        if "acao" in df_react.columns:
            display_cols.append("acao")
            col_config["acao"] = "🎯 Acção"

        if display_cols:
            st.dataframe(df_react[display_cols], use_container_width=True, hide_index=True, column_config=col_config)

    with col2:
        # Risk gauge
        by_type = pd.DataFrame(reactivation).groupby("tipo").agg(
            count=("cliente_id", "count"),
            valor=("valor_estimado", "sum")
        ).reset_index()

        type_labels = {"churn_risk": "⚠️ Risco Churn", "reactivation": "🔄 Reactivação"}
        by_type["label"] = by_type["tipo"].map(type_labels).fillna(by_type["tipo"])

        fig = go.Figure(data=[go.Bar(
            x=by_type["label"],
            y=by_type["valor"],
            marker_color=["#EF4444", "#F59E0B"][:len(by_type)],
            text=[f"€{v:,.0f}<br>{c} clientes" for v, c in zip(by_type["valor"], by_type["count"])],
            textposition="inside",
            textfont=dict(color="white", size=12),
        )])
        fig.update_layout(
            title="💸 Valor em Risco",
            xaxis_title="",
            yaxis=dict(gridcolor="#F1F5F9", tickprefix="€"),
            showlegend=False,
            **PLOTLY_LAYOUT
        )
        st.plotly_chart(fig, use_container_width=True)


def render_analysis(results, summary):
    """Deep analysis tab."""
    st.markdown("""
    <div class="section-header">
        <div class="section-icon">📈</div>
        <div>
            <h2 class="section-title">Análise Profunda</h2>
            <p class="section-desc">Tendências, padrões e métricas detalhadas</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    sales_df = results["sales_df"]

    # Summary metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📅 Período", f"{summary.get('periodo', {}).get('dias', 'N/A')} dias")
    c2.metric("📊 Transacções", f"{summary['transacoes']:,}")
    c3.metric("💰 Volume Total", f"€{summary['valor_total']:,.0f}")
    c4.metric("🧾 Ticket Médio", f"€{summary['ticket_medio']:,.0f}")

    col1, col2 = st.columns(2)

    with col1:
        # Heatmap: day of week x month
        sales_df_copy = sales_df.copy()
        if "data" in sales_df_copy.columns:
            sales_df_copy["weekday"] = sales_df_copy["data"].dt.day_name()
            sales_df_copy["month"] = sales_df_copy["data"].dt.strftime("%Y-%m")

            pivot = sales_df_copy.groupby(["weekday", "month"])["valor"].sum().reset_index()
            pivot_table = pivot.pivot(index="weekday", columns="month", values="valor").fillna(0)

            day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            pivot_table = pivot_table.reindex([d for d in day_order if d in pivot_table.index])

            fig = go.Figure(data=go.Heatmap(
                z=pivot_table.values,
                x=pivot_table.columns,
                y=pivot_table.index,
                colorscale=[[0, "#EFF6FF"], [0.5, "#3B82F6"], [1, "#1E3A5F"]],
                hovertemplate="Dia: %{y}<br>Mês: %{x}<br>Valor: €%{z:,.0f}<extra></extra>",
            ))
            fig.update_layout(
                title="🗓️ Heatmap de Vendas (Dia × Mês)",
                xaxis_title="", yaxis_title="",
                **PLOTLY_LAYOUT
            )
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Top products
        if "produto_nome" in sales_df.columns:
            prod_col = "produto_nome"
        elif "produto_id" in sales_df.columns:
            prod_col = "produto_id"
        else:
            prod_col = None

        if prod_col:
            top_prods = sales_df.groupby(prod_col)["valor"].sum().nlargest(10).reset_index()
            top_prods = top_prods.sort_values("valor", ascending=True)

            fig = go.Figure(data=[go.Bar(
                y=top_prods[prod_col].astype(str).str[:25],
                x=top_prods["valor"],
                orientation="h",
                marker=dict(color=top_prods["valor"], colorscale=[[0, "#6EE7B7"], [1, "#059669"]]),
                text=[f"€{v:,.0f}" for v in top_prods["valor"]],
                textposition="outside",
            )])
            fig.update_layout(
                title="📦 Top 10 Produtos",
                xaxis=dict(gridcolor="#F1F5F9", tickprefix="€"),
                **PLOTLY_LAYOUT,
                margin=dict(l=180, r=60, t=50, b=20),
            )
            st.plotly_chart(fig, use_container_width=True)

    # Clients by city
    customers_df = results["customers_df"]
    if customers_df is not None and "city" in customers_df.columns:
        city_data = customers_df["city"].value_counts().reset_index()
        city_data.columns = ["Cidade", "Clientes"]

        fig = go.Figure(data=[go.Bar(
            x=city_data["Cidade"][:15],
            y=city_data["Clientes"][:15],
            marker_color=COLORS["primary"],
            text=city_data["Clientes"][:15],
            textposition="outside",
        )])
        fig.update_layout(
            title="🗺️ Distribuição Geográfica de Clientes",
            xaxis_title="",
            yaxis=dict(gridcolor="#F1F5F9"),
            **PLOTLY_LAYOUT
        )
        st.plotly_chart(fig, use_container_width=True)


def render_report(results, summary):
    """Report tab."""
    st.markdown("""
    <div class="section-header">
        <div class="section-icon">📋</div>
        <div>
            <h2 class="section-title">Gerar Relatório</h2>
            <p class="section-desc">Export de dados e análises em formato profissional</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        report_format = st.radio("Formato do relatório", ["HTML", "Markdown"], horizontal=True)

        if st.button("📄 Gerar Relatório", type="primary", use_container_width=True):
            with st.spinner("Gerando relatório..."):
                generator = ReportGenerator()
                report = generator.generate_weekly_report(
                    opportunities=results["opportunities"],
                    rfm_summary=results["rfm_summary"],
                    format=report_format.lower()
                )

                st.success("✅ Relatório gerado com sucesso!")

                ext = "html" if report_format == "HTML" else "md"
                mime = "text/html" if report_format == "HTML" else "text/markdown"

                st.download_button(
                    label="⬇️ Download Relatório",
                    data=report,
                    file_name=f"aiti_insights_{datetime.now().strftime('%Y%m%d')}.{ext}",
                    mime=mime,
                    use_container_width=True,
                )

                if report_format == "HTML":
                    st.components.v1.html(report, height=600, scrolling=True)
                else:
                    st.markdown(report)

    with col2:
        st.markdown("""
        <div class="insight-card insight-card-highlight">
            <h4 style="margin: 0 0 0.75rem 0; color: #1E293B;">📑 O relatório inclui:</h4>
            <ul style="color: #475569; margin: 0; padding-left: 1.25rem; line-height: 1.8;">
                <li>KPIs e métricas principais</li>
                <li>Top oportunidades cross-sell</li>
                <li>Clientes para reactivação</li>
                <li>Análise de risco de churn</li>
                <li>Segmentação RFM completa</li>
                <li>Acções recomendadas</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="insight-card">
            <h4 style="margin: 0 0 0.5rem 0; color: #1E293B;">📊 Dados no relatório:</h4>
            <p style="color: #64748B; margin: 0; line-height: 1.6;">
                <strong>{summary['clientes_unicos']}</strong> clientes<br>
                <strong>{summary['transacoes']:,}</strong> transacções<br>
                <strong>{len(results['opportunities'])}</strong> oportunidades<br>
                <strong>€{summary['valor_total']:,.0f}</strong> volume total
            </p>
        </div>
        """, unsafe_allow_html=True)


def main():
    """Main app."""
    render_header()

    # Load data
    with st.spinner("🔄 Carregando dados..."):
        try:
            sales_df, customers_df, products_df, summary = load_demo_data()
        except Exception as e:
            st.error(f"Erro ao carregar dados: {e}")
            st.stop()

    # Sidebar
    min_support, min_confidence, min_value = render_sidebar(summary)

    # Run analysis
    with st.spinner("🧠 A IA está a analisar os dados..."):
        try:
            results = run_analysis(sales_df, customers_df, products_df, min_support, min_confidence, min_value)
        except Exception as e:
            st.error(f"Erro na análise: {e}")
            st.stop()

    # KPI Cards
    render_kpi_cards(summary, results["opportunities"], results["rules"])

    st.markdown("")

    # Main tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Visão Geral",
        "🛒 Cross-Sell",
        "👥 Segmentação RFM",
        "🔄 Reactivação",
        "📈 Análise Profunda",
    ])

    with tab1:
        render_overview(summary, results)

    with tab2:
        render_cross_sell(results)

    with tab3:
        render_rfm(results)

    with tab4:
        render_reactivation(results)

    with tab5:
        render_analysis(results, summary)

    # Report section (always visible)
    render_report(results, summary)

    # Footer
    st.markdown(f"""
    <div class="premium-footer">
        <strong>AITI Insights</strong> v2.0 Premium · Desenvolvido por <strong>AiParaTi</strong> · 
        Powered by Machine Learning · {datetime.now().strftime('%d/%m/%Y %H:%M')} UTC
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
