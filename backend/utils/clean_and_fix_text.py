import re
import html
import pandas as pd

def clean_and_fix_text(text):
    """
    Cleans and fixes encoding issues in the provided text.
    Handles null values, removes HTML tags, and corrects common Brazilian character encoding errors.
    """
    try:
        if text is None:
            return ""
        if pd.isna(text):
            return ""
    except (TypeError, ValueError):
        pass

    text = str(text)
    # Check for empty or placeholder strings
    if text.strip() in ("", "nan", "None", "NaN", "NaT"):
        return ""

    try:
        # Attempt to fix double encoding issues common in legacy exports
        text = text.encode('latin-1').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        # Fallback to manual correction for common broken character sequences
        corrections = {
            'Ãš': 'Ú', 'Ã§': 'ç', 'Ã£': 'ã', 'Ã©': 'é', 
            'Ã\xad': 'í', 'Ãª': 'ê', 'Ã¡': 'á', 'Ãµ': 'õ', 
            'Ã³': 'ó', 'Ã¢': 'â', 'Ã\x87': 'Ç', 'Ã\x83': 'Ã', 
            'Ã•': 'Õ', 'Ã‰': 'É', 'Ã ': 'À', 'Ã\x8d': 'Í', 
            'Ã\x93': 'Ó', 'Ã\x82': 'Â', 'Ã\x8a': 'Ê'
        }
        for wrong, right in corrections.items():
            text = text.replace(wrong, right)

    # Decode HTML entities and strip tags
    text = html.unescape(text)
    text = re.sub(r'<[^>]+>', ' ', text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    text = text.strip('"').strip("'")

    return text