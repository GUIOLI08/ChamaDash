from google.auth import api_key
from typing import Any, Dict
from google import genai
from config.ia import CONFIG_IA
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("API_KEY")

def consult_ia(dados_resumo: Dict[str, Any]) -> Dict[str, str]:
    """
    Conecta-se com o provedor de IA para gerar introduções de relatórios e análises de dados.

    Se a chave da API não estiver configurada (valor de placeholder), retorna textos estáticos predefinidos.

    Args:
        dados_resumo (Dict[str, Any]): Dicionário contendo os dados sumarizados do dashboard (SLA, tipos, etc).

    Returns:
        Dict[str, str]: Dicionário com as chaves 'introduction' e 'data_analysis' contendo os textos gerados.
    """
    
    # Verifica se a chave de API é válida
    if not CONFIG_IA["api_key"] or CONFIG_IA["api_key"] == "SUA_CHAVE_AQUI" or CONFIG_IA["api_key"] == "YOUR_API_KEY_HERE":
        return {
            "introduction": "[IA DESATIVADA] - Erro ao tentar gerar a introdução.",
            "data_analysis": "[IA DESATIVADA] - Erro ao tentar gerar a análise de dados."
        }

    try:
        if CONFIG_IA["provider"] == "gemini":
            client = genai.Client(api_key=CONFIG_IA["api_key"])
            
            prompt = f"""
            Você é um gerente de TI analisando resultados de Service Desk. Analise estes dados:
            - SLA de Atendimento: {dados_resumo.get('sla', 'N/A')}
            - Distribuição por Tipo: {dados_resumo.get('tipos_gerais', 'N/A')}
            
            Escreva um relatório executivo formal e direto. Retorne a resposta ESTRITAMENTE neste formato, usando as tags:
            
            [INTRODUCAO]
            (Escreva 1 parágrafo introdutório apresentando o objetivo do relatório e um resumo rápido do cenário do mês)
            
            [DADOS_GERAIS]
            (Escreva 1 a 2 parágrafos analisando os dados acima, destacando o percentual de SLA atingido e o volume principal de tipos de chamados.)
            """
            
            response = client.models.generate_content(
                model=CONFIG_IA["model"],
                contents=prompt,
            )
            
            raw_response = response.text
            
            # Analisa a resposta da IA usando os marcadores definidos no prompt
            introduction = raw_response.split("[INTRODUCAO]")[1].split("[DADOS_GERAIS]")[0].strip() if "[INTRODUCAO]" in raw_response else "Erro ao gerar a introdução."
            data_analysis = raw_response.split("[DADOS_GERAIS]")[1].strip() if "[DADOS_GERAIS]" in raw_response else "Erro ao gerar a análise."
            
            return {"introduction": introduction, "data_analysis": data_analysis}
            
    except Exception as e:
        # Log de erro e retorno de um fallback seguro para evitar crash no servidor
        print(f"⚠️ Erro ao consultar a IA: {e}")
        return {"introduction": "Erro na IA.", "data_analysis": f"Detalhe do erro: {e}"}
    
    return {"introduction": "Provedor de IA não suportado.", "data_analysis": "N/A"}
