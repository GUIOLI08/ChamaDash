import re
import html
import pandas as pd

def clean_and_fix_text(text):
    if pd.isna(text):
        return text
    
    text = str(text)

    try:
        text = text.encode('latin-1').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        corrections = {
            'Ãš': 'Ú', 'Ã§': 'ç', 'Ã£': 'ã', 'Ã©': 'é', 
            'Ã\xad': 'í', 'Ãª': 'ê', 'Ã¡': 'á', 'Ãµ': 'õ', 
            'Ã³': 'ó', 'Ã¢': 'â', 'Ã\x87': 'Ç', 'Ã\x83': 'Ã', 
            'Ã•': 'Õ', 'Ã‰': 'É', 'Ã ': 'À', 'Ã\x8d': 'Í', 
            'Ã\x93': 'Ó', 'Ã\x82': 'Â', 'Ã\x8a': 'Ê'
        }
        for wrong, right in corrections.items():
            text = text.replace(wrong, right)

    text = html.unescape(text) 
    text = re.sub(r'<[^>]+>', ' ', text) 
    text = re.sub(r'\s+', ' ', text).strip() 

    text = text.strip('"').strip("'")
        
    return text