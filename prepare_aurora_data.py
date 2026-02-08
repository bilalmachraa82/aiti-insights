#!/usr/bin/env python3
"""
Script para converter dados Aurora Oceano (JSON) para CSVs do AITI-INSIGHTS
"""

import json
import pandas as pd
from datetime import datetime, timedelta
import random
import os
from pathlib import Path

# Diretórios
AURORA_DIR = Path("../aurora-oceano/dashboard-real/data")
OUTPUT_DIR = Path("data/demo")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def load_json(filename):
    """Carrega JSON de Aurora Oceano"""
    path = AURORA_DIR / filename
    if not path.exists():
        print(f"⚠️  {filename} não encontrado")
        return []
    
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def prepare_clientes():
    """Prepara arquivo clientes.csv"""
    print("📊 Preparando clientes...")
    
    raw_clientes = load_json('clientes.json')
    if not raw_clientes:
        print("❌ Sem dados de clientes")
        return None
    
    # Mapear segmentos por tamanho/tipo
    segmentacao = {
        "Restaurante": "Horeca",
        "Hotel": "Horeca",
        "Bar": "Horeca",
        "Café": "Horeca",
        "Lda": "Distribuição",
        "distribui": "Distribuição",
        "Comércio": "Distribuição",
        "empresa": "Empresa",
    }
    
    clientes_data = []
    for cliente in raw_clientes:
        nome_upper = cliente['name'].upper()
        
        # Classificar segmento
        segmento = "Outro"
        for keyword, seg in segmentacao.items():
            if keyword.upper() in nome_upper:
                segmento = seg
                break
        
        # Região baseada em city
        regiao = cliente.get('city', 'Portugal').split()[0] if cliente.get('city') else 'Portugal'
        
        clientes_data.append({
            'cliente_id': cliente['customer_id'],
            'nome': cliente['name'][:50],  # Limitar tamanho
            'segmento': segmento,
            'regiao': regiao,
            'cidade': cliente.get('city', '')
        })
    
    df = pd.DataFrame(clientes_data)
    df = df.drop_duplicates(subset=['cliente_id'])
    
    print(f"✅ {len(df)} clientes únicos")
    return df

def prepare_produtos():
    """Prepara arquivo produtos.csv"""
    print("📦 Preparando produtos...")
    
    raw_produtos = load_json('produtos.json')
    if not raw_produtos:
        print("❌ Sem dados de produtos")
        return None
    
    # Categorias baseadas em nomes
    categoria_map = {
        "bacalhau": "Peixe",
        "camarão": "Frutos do Mar",
        "gambas": "Frutos do Mar",
        "azeite": "Azeite",
        "sal": "Sal",
        "tempero": "Temperos",
        "vinho": "Bebidas",
        "cerveja": "Bebidas",
        "refrigerante": "Bebidas",
        "agua": "Bebidas",
        "pão": "Padaria",
        "queijo": "Lacticínios",
        "leite": "Lacticínios",
        "manteiga": "Lacticínios",
        "carne": "Carnes",
        "frango": "Carnes",
        "porco": "Carnes",
    }
    
    produtos_data = []
    for produto in raw_produtos[:100]:  # Limitar a 100 produtos
        nome = produto.get('name', '')
        nome_lower = nome.lower()
        
        # Classificar categoria
        categoria = "Alimentos"
        for keyword, cat in categoria_map.items():
            if keyword in nome_lower:
                categoria = cat
                break
        
        preco = produto.get('price', 0) or random.uniform(5, 100)
        
        produtos_data.append({
            'produto_id': produto.get('product_id', produto.get('id', '')),
            'nome': nome[:50],
            'categoria': categoria,
            'preco_unitario': float(preco)
        })
    
    df = pd.DataFrame(produtos_data)
    df = df.drop_duplicates(subset=['produto_id'])
    
    print(f"✅ {len(df)} produtos únicos")
    return df

def prepare_vendas(clientes_df, produtos_df):
    """Prepara arquivo vendas.csv baseado em faturas"""
    print("💰 Preparando vendas...")
    
    raw_faturas = load_json('faturas.json')
    if not raw_faturas:
        print("❌ Sem dados de faturas")
        return None
    
    # Criar mapa de IDs válidos
    cliente_ids = set(clientes_df['cliente_id'].unique())
    produto_ids = set(produtos_df['produto_id'].unique())
    
    vendas_data = []
    
    for fatura in raw_faturas:
        cliente_id = fatura.get('customer_id')
        if cliente_id not in cliente_ids:
            continue
        
        # Extrair data da fatura
        data_str = fatura.get('date', '')
        try:
            data = pd.to_datetime(data_str).date()
        except:
            data = pd.Timestamp.now().date()
        
        valor_total = fatura.get('total', 0) or random.uniform(50, 500)
        
        # Simular produtos (usar produtos aleatórios)
        num_produtos = random.randint(1, 5)
        for _ in range(num_produtos):
            produto_id = random.choice(list(produto_ids))
            quantidade = random.randint(1, 10)
            valor_linha = valor_total / num_produtos
            
            vendas_data.append({
                'data': data,
                'cliente_id': cliente_id,
                'produto_id': produto_id,
                'quantidade': quantidade,
                'valor': valor_linha
            })
    
    df = pd.DataFrame(vendas_data)
    
    # Manter apenas últimos 12 meses
    df['data'] = pd.to_datetime(df['data'])
    cutoff = pd.Timestamp.now() - timedelta(days=365)
    df = df[df['data'] >= cutoff]
    
    print(f"✅ {len(df)} linhas de vendas")
    return df

def main():
    print("\n🚀 Convertendo dados Aurora Oceano para AITI-INSIGHTS\n")
    
    # Preparar dados
    clientes_df = prepare_clientes()
    produtos_df = prepare_produtos()
    
    if clientes_df is None or produtos_df is None:
        print("❌ Erro ao preparar dados")
        return False
    
    vendas_df = prepare_vendas(clientes_df, produtos_df)
    
    if vendas_df is None:
        print("❌ Erro ao preparar vendas")
        return False
    
    # Salvar CSVs
    print("\n💾 Salvando CSVs...")
    
    clientes_path = OUTPUT_DIR / "clientes.csv"
    clientes_df.to_csv(clientes_path, index=False, encoding='utf-8')
    print(f"✅ {clientes_path}")
    
    produtos_path = OUTPUT_DIR / "produtos.csv"
    produtos_df.to_csv(produtos_path, index=False, encoding='utf-8')
    print(f"✅ {produtos_path}")
    
    vendas_path = OUTPUT_DIR / "vendas.csv"
    vendas_df.to_csv(vendas_path, index=False, encoding='utf-8')
    print(f"✅ {vendas_path}")
    
    print("\n📊 RESUMO")
    print(f"  • Clientes: {len(clientes_df)}")
    print(f"  • Produtos: {len(produtos_df)}")
    print(f"  • Vendas: {len(vendas_df)}")
    print(f"  • Período: {vendas_df['data'].min()} até {vendas_df['data'].max()}")
    print(f"  • Valor total: €{vendas_df['valor'].sum():.2f}")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
