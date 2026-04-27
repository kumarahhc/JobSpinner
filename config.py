import os
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

PROXY_URL = os.getenv("API_PROXY")

#----------- LLM CONFIGURATION -----------

LLM_CONFIG = {
    "config_list": [
        {
            "model": "openai/gpt-4.1-mini",
            "api_key": "not-needed",
            "base_url": PROXY_URL
        }
    ],
    "temperature": 0.2,
    "timeout": 120,
    "cache_seed": None
}

#----------- TAVILY CONFIGURATION -----------
TAVILY_CONFIG = {
    "api_key": os.getenv("TAVILY_API_KEY"),
    "base_url": PROXY_URL
}

#----------- OUTPUT FOLDER ----------------
OUTPUT_FOLDER = "output"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)