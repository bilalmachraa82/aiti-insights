#!/bin/bash
# Script de Deploy AITI Insights para Streamlit Cloud

set -e

echo "🚀 AITI Insights - Deploy para Streamlit Cloud"
echo "=============================================="
echo ""

# Verificar se estamos no diretório correto
if [ ! -f "src/aiti_insights/dashboard.py" ]; then
    echo "❌ Erro: Execute este script a partir do diretório raiz do projeto"
    exit 1
fi

# Verificar se o Git está configurado
if [ -z "$(git config user.email)" ]; then
    echo "⚠️  Configure seu Git primeiro:"
    echo "   git config --global user.email 'seu@email.com'"
    echo "   git config --global user.name 'Seu Nome'"
    exit 1
fi

# Ativar venv
echo "📦 Ativando ambiente virtual..."
source venv/bin/activate 2>/dev/null || python -m venv venv && source venv/bin/activate

# Instalar dependências
echo "📚 Instalando dependências..."
pip install -q -r requirements.txt

# Testar localmente
echo ""
echo "🧪 Testando dashboard localmente (5 segundos)..."
timeout 5 streamlit run src/aiti_insights/dashboard.py --logger.level=error || true

# Verificar GitHub
echo ""
echo "📤 Verificando status do Git..."
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  Existem mudanças não commitadas."
    echo "   Commit: git add -A && git commit -m 'tua mensagem'"
    exit 1
fi

# Verificar branch
BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$BRANCH" != "main" ]; then
    echo "⚠️  Você está na branch '$BRANCH', não em 'main'"
    echo "   Deploy recomendado a partir de 'main'"
    exit 1
fi

echo ""
echo "✅ Tudo OK! Agora faça deploy manualmente:"
echo ""
echo "1. Aceda a: https://streamlit.io/cloud"
echo "2. Clique em 'New app'"
echo "3. Selecione repositório: bilalmachraa82/aiti-insights"
echo "4. Configurar:"
echo "   - Branch: main"
echo "   - Main file: src/aiti_insights/dashboard.py"
echo "5. Clique em 'Deploy'"
echo ""
echo "ou tente com credenciais pré-configuradas:"
echo "   streamlit deploy"
echo ""
echo "URL esperado: https://aiti-insights.streamlit.app"
echo ""
