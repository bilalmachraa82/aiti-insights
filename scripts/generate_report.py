#!/usr/bin/env python3
"""
Generate weekly opportunity report from command line.

Usage:
    python generate_report.py [--output report.html] [--format html|markdown]
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from aiti_insights.etl import ETLProcessor
from aiti_insights.apriori import AprioriAnalyzer
from aiti_insights.rfm import RFMAnalyzer
from aiti_insights.opportunities import OpportunityEngine
from aiti_insights.reports import ReportGenerator


def main():
    parser = argparse.ArgumentParser(description="Generate AITI Insights Report")
    parser.add_argument("--sales", help="Path to sales CSV/Excel", default=None)
    parser.add_argument("--customers", help="Path to customers CSV/Excel", default=None)
    parser.add_argument("--products", help="Path to products CSV/Excel", default=None)
    parser.add_argument("--output", "-o", help="Output file path", default=None)
    parser.add_argument("--format", "-f", choices=["html", "markdown"], default="html")
    
    args = parser.parse_args()
    
    # Load data
    print("📂 Loading data...")
    
    data_dir = Path(__file__).parent.parent / "data" / "demo"
    etl = ETLProcessor()
    
    if args.sales:
        sales_df = etl.load_sales(args.sales)
    else:
        sales_df = etl.load_sales(data_dir / "vendas.csv")
    
    if args.customers:
        customers_df = etl.load_customers(args.customers)
    else:
        customers_df = etl.load_customers(data_dir / "clientes.csv")
    
    if args.products:
        products_df = etl.load_products(args.products)
    else:
        products_df = etl.load_products(data_dir / "produtos.csv")
    
    summary = etl.get_summary()
    print(f"   ✅ {summary['transacoes']} transactions, {summary['clientes_unicos']} customers")
    
    # Run Apriori
    print("🔍 Running Apriori analysis...")
    apriori = AprioriAnalyzer(min_support=0.02, min_confidence=0.3)
    rules = apriori.analyze(sales_df)
    print(f"   ✅ Found {len(rules)} association rules")
    
    # Run RFM
    print("📊 Running RFM segmentation...")
    rfm = RFMAnalyzer()
    rfm_df = rfm.analyze(sales_df)
    rfm_summary = rfm.get_segment_summary()
    print(f"   ✅ Segmented {len(rfm_df)} customers")
    
    # Generate opportunities
    print("🎯 Generating opportunities...")
    engine = OpportunityEngine(min_value=50)
    opportunities = engine.generate(
        sales_df=sales_df,
        rules=rules,
        rfm_segments=rfm_df,
        customers_df=customers_df,
        products_df=products_df
    )
    
    opp_summary = engine.get_summary()
    print(f"   ✅ Found {opp_summary['total_oportunidades']} opportunities")
    print(f"   💰 Total potential: €{opp_summary['valor_total_estimado']:,.0f}")
    
    # Generate report
    print("📄 Generating report...")
    
    if args.output:
        output_path = args.output
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        ext = "html" if args.format == "html" else "md"
        output_path = f"aiti_insights_report_{timestamp}.{ext}"
    
    generator = ReportGenerator()
    report = generator.generate_weekly_report(
        opportunities=opportunities,
        rfm_summary=rfm_summary,
        output_path=output_path,
        format=args.format
    )
    
    print(f"   ✅ Report saved to: {output_path}")
    print("")
    print("=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    print(f"Total Opportunities: {opp_summary['total_oportunidades']}")
    print(f"Potential Value: €{opp_summary['valor_total_estimado']:,.0f}")
    print(f"Cross-sell: {opp_summary['por_tipo'].get('cross_sell', {}).get('count', 0)}")
    print(f"Reactivation: {opp_summary['por_tipo'].get('reactivation', {}).get('count', 0)}")
    print(f"Churn Risk: {opp_summary['por_tipo'].get('churn_risk', {}).get('count', 0)}")
    print("=" * 50)


if __name__ == "__main__":
    main()
