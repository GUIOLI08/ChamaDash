"""
Módulo de configuração para o provedor de IA.
Centraliza as chaves de API e configurações do modelo Gemini.
"""

import os

# Configurações do Provedor de IA
# Este dicionário centraliza as definições para a API do Google Gemini.
CONFIG_IA = {
    "provider": "gemini",
    "api_key": os.environ.get("API_KEY", "AIzaSyCpNMi0u5Zc1c7Bq6mL9fyAKtMzCR3Cmos"),
    "model": "gemini-2.0-flash"  # Versão estável do modelo para resultados consistentes
}