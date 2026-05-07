import os
from dotenv import load_dotenv

load_dotenv()

# Google Gemini API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Discord Webhook URL
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# Forex Factory URL (market-specific page for GOLD/USD)
FOREX_FACTORY_URL = "https://www.forexfactory.com/market/goldusd"
