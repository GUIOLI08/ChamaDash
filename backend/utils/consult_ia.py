from google import genai

from config.ia import CONFIG_IA

def consult_ia(dados_resumo):
    """
    Connects with the AI provider to generate report introductions and data analyses.
    If the API key is not configured (placeholder value), returns preset static text.
    """
    if not CONFIG_IA["api_key"] or CONFIG_IA["api_key"] == "AIzaSyCpNMi0u5Zc1c7Bq6mL9fyAKtMzCR3Cmos":
        return {
            "introduction": "[IA DESATIVADA] - Insira sua chave API no código para gerar a introdução automática.",
            "data_analysis": "[IA DESATIVADA] - Insira sua chave API no código para gerar a análise de dados automática."
        }

    try:
        if CONFIG_IA["provider"] == "gemini":
            client = genai.Client(api_key=CONFIG_IA["api_key"])
            
            prompt = f"""
            Você é um gerente de TI analisando resultados de Service Desk. Analise estes dados:
            - SLA de Atendimento: {dados_resumo['sla']}
            - Distribuição por Tipo: {dados_resumo['tipos_gerais']}
            
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
            
            # Parse the AI response using markers defined in the prompt
            introduction = raw_response.split("[INTRODUCAO]")[1].split("[DADOS_GERAIS]")[0].strip() if "[INTRODUCAO]" in raw_response else "Error generating introduction."
            data_analysis = raw_response.split("[DADOS_GERAIS]")[1].strip() if "[DADOS_GERAIS]" in raw_response else "Error generating analysis."
            
            return {"introduction": introduction, "data_analysis": data_analysis}
            
    except Exception as e:
        # Logging error and returning a safe fallback to prevent server crash
        print(f"⚠️ Error consulting AI: {e}")
        return {"introduction": "Erro na IA.", "data_analysis": f"Detalhe do erro: {e}"}