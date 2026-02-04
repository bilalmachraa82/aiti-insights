# 🎯 AITI Insights - Motor de Oportunidades Comerciais

**Transforme dados históricos de vendas em acções comerciais concretas.**

Sistema de análise preditiva que identifica oportunidades escondidas: cross-sell, upsell, reactivação de clientes e previsão de churn.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🚀 Funcionalidades

### ✅ MVP (v1.0)
- **ETL Universal**: Importação de CSV/Excel com normalização automática
- **Análise Apriori**: Regras de associação para cross-sell ("Quem compra A, compra B")
- **Segmentação RFM**: Champions, At Risk, Dormentes, etc.
- **Dashboard Interactivo**: Streamlit com KPIs e oportunidades
- **Relatório Semanal**: Exportação automática de oportunidades

### 🔜 Roadmap
- [ ] Previsão de Churn (ML)
- [ ] Campanhas automáticas (n8n + Email)
- [ ] Integração CRM (HubSpot, Pipedrive)
- [ ] API REST

---

## 📊 Screenshots

### Dashboard Principal
```
┌─────────────────────────────────────────────────────────────┐
│  AITI INSIGHTS - Motor de Oportunidades                     │
├─────────────────────────────────────────────────────────────┤
│  💰 €152.000      👥 420        🎯 68         📈 +15%       │
│  Potencial        Clientes      Oportunidades  Cross-sell   │
├─────────────────────────────────────────────────────────────┤
│  TOP OPORTUNIDADES CROSS-SELL                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ 1. Restaurante Silva │ Bacalhau → Azeite │ €8.500 68% │ │
│  │ 2. Hotel Mar Azul    │ Camarão → Gambas  │ €6.200 72% │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                             │
│  SEGMENTAÇÃO RFM                                            │
│  [██████████] Champions: 85 (20%)                          │
│  [████████  ] Loyal: 63 (15%)                              │
│  [██████    ] At Risk: 42 (10%)                            │
│  [████      ] Dormant: 21 (5%)                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Instalação

### Pré-requisitos
- Python 3.10+
- pip

### Setup Rápido

```bash
# Clonar repositório
git clone https://github.com/bilalmachraa82/aiti-insights.git
cd aiti-insights

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Executar dashboard com dados demo
streamlit run src/aiti_insights/dashboard.py
```

O dashboard estará disponível em `http://localhost:8501`

---

## 📁 Estrutura do Projecto

```
aiti-insights/
├── src/
│   └── aiti_insights/
│       ├── __init__.py
│       ├── etl.py              # Importação de dados
│       ├── apriori.py          # Análise de associação
│       ├── rfm.py              # Segmentação RFM
│       ├── opportunities.py    # Motor de oportunidades
│       ├── reports.py          # Geração de relatórios
│       └── dashboard.py        # Interface Streamlit
├── data/
│   └── demo/
│       ├── vendas.csv          # Dados de exemplo
│       ├── clientes.csv
│       └── produtos.csv
├── tests/
├── docs/
├── scripts/
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## 📊 Dados de Entrada

### Formato Esperado

#### vendas.csv
| Campo | Tipo | Descrição |
|-------|------|-----------|
| data | date | Data da venda (YYYY-MM-DD) |
| cliente_id | string/int | ID único do cliente |
| produto_id | string/int | ID único do produto |
| quantidade | int | Quantidade vendida |
| valor | float | Valor total da linha |

#### clientes.csv (opcional)
| Campo | Tipo | Descrição |
|-------|------|-----------|
| cliente_id | string/int | ID único |
| nome | string | Nome do cliente |
| segmento | string | Segmento de mercado |
| regiao | string | Região geográfica |

#### produtos.csv (opcional)
| Campo | Tipo | Descrição |
|-------|------|-----------|
| produto_id | string/int | ID único |
| nome | string | Nome do produto |
| categoria | string | Categoria |
| preco_unitario | float | Preço médio |

---

## 🎯 Algoritmos

### 1. Apriori (Cross-Sell)
Identifica regras de associação entre produtos:
```python
# Output exemplo
{
    "antecedente": ["Bacalhau Seco"],
    "consequente": ["Azeite Virgem Extra"],
    "suporte": 0.15,
    "confiança": 0.68,
    "lift": 2.3
}
```

### 2. RFM (Segmentação)
Classifica clientes por Recência, Frequência e Valor Monetário:

| Segmento | Descrição | Acção |
|----------|-----------|-------|
| Champions | Compram frequentemente, gastam muito | Premiar |
| Loyal | Bons clientes regulares | Manter |
| At Risk | Eram bons, reduziram actividade | Recuperar |
| Hibernating | Compraram há muito tempo | Reactivar |
| Lost | Perdidos há >12 meses | Campanha especial |

---

## 🔧 Configuração

### Variáveis de Ambiente (opcional)

```bash
# .env
DATABASE_URL=postgresql://user:pass@host/db  # Se usar PostgreSQL
MIN_SUPPORT=0.05      # Suporte mínimo Apriori
MIN_CONFIDENCE=0.5    # Confiança mínima
```

---

## 📈 ROI Esperado

| Oportunidade | Impacto Típico |
|--------------|----------------|
| Cross-sell identificado | +15-25% revenue |
| Reactivação dormentes | 20-30% retornam |
| Prevenção churn | 15% LTV preservado |

**Exemplo real**: Distribuidor com 420 clientes e €2M/ano identificou €152.000 em oportunidades.

---

## 🤝 Contribuir

1. Fork o repositório
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

---

## 📝 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

---

## 👥 Autores

- **AiParaTi** - [aiparati.pt](https://aiparati.pt)
- **Bilal Machraa** - [@bilalmachraa82](https://github.com/bilalmachraa82)

---

## 🔗 Links

- [Documentação Completa](docs/)
- [Changelog](CHANGELOG.md)
- [Reportar Bug](https://github.com/bilalmachraa82/aiti-insights/issues)

---

*Desenvolvido com ❤️ em Portugal*
