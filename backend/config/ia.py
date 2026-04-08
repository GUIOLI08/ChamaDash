"""
Módulo de configuração para o provedor de IA.
Centraliza as chaves de API e configurações do modelo Gemini.
"""

import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("API_KEY")

# Configurações do Provedor de IA
# Este dicionário centraliza as definições para a API do Google Gemini.
CONFIG_IA = {
    "provider": "gemini",
    "api_key": api_key,
    "model": "gemini-3-flash"  # Versão estável do modelo para resultados consistentes
}