from typing import Optional
import re
import html
import pandas as pd

def clean_and_fix_text(text: Optional[str]) -> str:
    """
    Limpa e corrige problemas de codificação no texto fornecido.

    Lida com valores nulos, remove tags HTML e corrige erros comuns de codificação 
    de caracteres brasileiros (UTF-8/Latin-1).

    Args:
        text (Optional[str]): O texto original que precisa de limpeza.

    Returns:
        str: O texto limpo e corrigido. Retorna uma string vazia se o input for inválido.
    """
    try:
        if text is None:
            return ""
        if pd.isna(text):
            return ""
    except (TypeError, ValueError):
        pass

    text = str(text)
    # Verifica se a string está vazia ou contém marcadores de valor nulo
    if text.strip() in ("", "nan", "None", "NaN", "NaT"):
        return ""

    try:
        # Tenta corrigir problemas de "double encoding" comuns em exportações Legacy
        text = text.encode('latin-1').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        # Fallback para correção manual de sequências de caracteres quebrados comuns
        corrections = {
            'Ãš': 'Ú', 'Ã§': 'ç', 'Ã£': 'ã', 'Ã©': 'é', 
            'Ã\xad': 'í', 'Ãª': 'ê', 'Ã¡': 'á', 'Ãµ': 'õ', 
            'Ã³': 'ó', 'Ã¢': 'â', 'Ã\x87': 'Ç', 'Ã\x83': 'Ã', 
            'Ã•': 'Õ', 'Ã‰': 'É', 'Ã ': 'À', 'Ã\x8d': 'Í', 
            'Ã\x93': 'Ó', 'Ã\x82': 'Â', 'Ã\x8a': 'Ê'
        }
        for wrong, right in corrections.items():
            text = text.replace(wrong, right)

    # Decodifica entidades HTML e remove tags
    text = html.unescape(text)
    text = re.sub(r'<[^>]+>', ' ', text)
    # Normaliza espaços em branco
    text = re.sub(r'\s+', ' ', text).strip()
    text = text.strip('"').strip("'")

    return text