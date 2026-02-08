# 🚀 Deploy no Streamlit Cloud - AITI Insights

## Status Atual ✅

- ✅ Repositório: `github.com/bilalmachraa82/aiti-insights`
- ✅ Dados Aurora Oceano: Convertidos e atualizados
- ✅ Dashboard testado localmente: **FUNCIONANDO**
- ✅ Código commitado ao GitHub

## Dados Carregados 📊

| Métrica | Valor |
|---------|-------|
| **Clientes** | 50 únicos |
| **Produtos** | 50 únicos |
| **Vendas** | 16 transações |
| **Valor Total** | €977.08 |
| **Período** | 28-29 Jan 2026 |

## Passo 1: Acesso ao Streamlit Cloud

1. Ir para: https://streamlit.io/cloud
2. Fazer login com conta GitHub (ou criar uma)
3. Clicar em **"New app"**

## Passo 2: Conectar Repositório

- **Repository**: `bilalmachraa82/aiti-insights`
- **Branch**: `main`
- **Main file path**: `src/aiti_insights/dashboard.py`

## Passo 3: Configurar Secrets (se necessário)

Se o dashboard precisar de variáveis de ambiente:

```
[streamlit]
theme = "light"

[client]
showErrorDetails = true

[server]
runOnSave = true
```

**Secrets (em .streamlit/secrets.toml no Streamlit Cloud):**
```
# Deixar vazio por enquanto - dados são carregados localmente
```

## Passo 4: Deploy

Clicar em **"Deploy"** e aguardar (~2-3 minutos)

## URL Esperado

```
https://aiti-insights-[random].streamlit.app
```

## Teste Local (antes do deploy)

```bash
cd ~/clawd/projects/aiti-insights
source venv/bin/activate
streamlit run src/aiti_insights/dashboard.py
```

Aceder a: http://localhost:8501

## 📈 Funcionalidades da Dashboard

### 1. **KPIs Principais** 
- Potencial de oportunidades (€)
- Total de clientes
- Cross-sell identificadas
- Lift médio

### 2. **Análise Apriori**
- Regras de associação entre produtos
- Visualização de confiança e suporte
- Top 10 oportunidades de cross-sell

### 3. **Segmentação RFM**
- Champions, Loyal, At Risk, Dormant, Lost
- Gráficos interativos
- Distribuição por segmento

### 4. **Oportunidades Comerciais**
- Lista de clientes com potencial
- Valor estimado por oportunidade
- Tipo de oportunidade (cross-sell, upsell, reactivação)

## 📝 Troubleshooting

### Error: "Data not found"
```
Solução: Executar prepare_aurora_data.py
python prepare_aurora_data.py
```

### Error: "Module not found"
```
Solução: Criar arquivo requirements.txt correto
pip install -r requirements.txt
```

### Dashboard em branco
```
Solução: Verificar logs no Streamlit Cloud:
Settings → View logs
```

## 🔗 GitHub Actions (CI/CD - Opcional)

Se quiser auto-deploy ao fazer push:

1. Ir a Streamlit Cloud → Settings → GitHub Connection
2. Selecionar "Deploy on every push to main"

## 📧 Contato Demo

Quando o demo estiver LIVE:
- **URL**: [será gerada pelo Streamlit Cloud]
- **Dados**: Aurora Oceano (Real)
- **Atualização**: Manual (executar `prepare_aurora_data.py`)

---

**Criado em**: 2026-02-08 20:46 UTC  
**Por**: JARVIS (Subagent Deploy)  
**Status**: Pronto para deploy ✅
