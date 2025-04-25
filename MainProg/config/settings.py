"""
Application settings and configuration.
"""
import os
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

# API Settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEFAULT_MODEL = "gpt-3.5-turbo"
API_MAX_RETRIES = 3
API_TIMEOUT = 30

# App Settings
DEFAULT_TEMPERATURE = 0.7
DEFAULT_TOP_P = 0.9
DEFAULT_FONT_SIZE = 16
DEFAULT_WORD_COUNT = 500

# UI Settings
PRIMARY_COLOR = "#4F8BF9"
SECONDARY_COLOR = "#FF4B4B"
ACCENT_COLOR = "#F0F2F6"