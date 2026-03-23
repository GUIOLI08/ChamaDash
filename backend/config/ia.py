import os

# AI Configuration
CONFIG_IA = {
    "provider": "gemini",
    "api_key": os.environ.get("API_KEY", "AIzaSyCpNMi0u5Zc1c7Bq6mL9fyAKtMzCR3Cmos"),
    "model": "gemini-2.5-flash" # Fixed model version
}