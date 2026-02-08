#!/usr/bin/env python
"""
AITI Insights - Streamlit App Entry Point
==========================================

Este ficheiro é o ponto de entrada para o Streamlit Cloud.
Importa e executa o dashboard a partir de src/aiti_insights/dashboard.py

Para executar localmente:
    streamlit run streamlit_app.py

Para deploy no Streamlit Cloud:
    Main file path: streamlit_app.py
"""

import sys
from pathlib import Path

# Adicionar src ao path para importações
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

# Importar e executar o dashboard
from aiti_insights.dashboard import main

if __name__ == "__main__":
    main()
