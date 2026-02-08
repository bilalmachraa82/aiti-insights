# ⏱️ Deploy AITI-Insights: Checklist 2 Minutos

**Tudo pronto!** Siga estes passos para fazer deploy no Streamlit Cloud.

---

## 🚀 Checklist (2 Minutos Total)

### [ ] 0-30s: Acesso Streamlit Cloud
- [ ] Abrir: https://streamlit.io/cloud
- [ ] Clicar "Sign in with GitHub"
- [ ] Autorizar/fazer login

### [ ] 30s-1m30s: Criar App
- [ ] Clicar "New app"
- [ ] Preencher:
  - **Repository**: bilalmachraa82/aiti-insights
  - **Branch**: main
  - **Main file path**: `streamlit_app.py` ← **IMPORTANTE!**
- [ ] Clicar "Deploy"

### [ ] 1m30s-2m: Aguardar
- [ ] Streamlit faz build
- [ ] Recebe mensagem: "App deployed successfully"
- [ ] Copia URL: https://aiti-insights-XXXXX.streamlit.app

### [ ] 2m+: Testar (15 segundos extra)
- [ ] Abre URL no browser
- [ ] Verifica se aparecem os gráficos
- [ ] Clica em alguns filtros para confirmar

---

## ✅ Quando Terminar

1. **Copiar URL**: `https://aiti-insights-XXXXX.streamlit.app`
2. **Partilhar com**: Fernando/CTO ou quem for
3. **Demo está LIVE!** 🎉

---

## ⚠️ Se Não Funcionar

| Erro | Solução |
|------|---------|
| "Module not found" | Verificar Main file: `streamlit_app.py` |
| "Data not found" | Dados estão em data/demo/ - OK |
| Dashboard em branco | Clique Settings → View logs no Streamlit Cloud |
| GitHub connection error | Dar permissões ao Streamlit no GitHub |

---

## 📊 O Que Verá

Quando a app carregar, verá:
- ✅ KPIs: Potencial €, Oportunidades, Clientes, Produtos
- ✅ Gráficos: Cross-sell, RFM, Oportunidades
- ✅ Filtros no sidebar para explorar dados
- ✅ Dados reais da Aurora Oceano

---

**Tempo Total: 2 minutos** ⏱️  
**Dificuldade: Muito Fácil** ⭐⭐☆☆☆  
**Criado por**: Subagente Deploy-Insights
