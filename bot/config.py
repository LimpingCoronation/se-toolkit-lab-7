"""Configuration loader for the bot."""

import os
from pathlib import Path
from dotenv import load_dotenv


def load_config() -> dict[str, str]:
    """Load configuration from .env.bot.secret file.
    
    Returns a dict with keys:
        BOT_TOKEN, LMS_API_URL, LMS_API_KEY, LLM_API_KEY, 
        LLM_API_BASE_URL, LLM_API_MODEL
    """
    # Path to .env.bot.secret in the project root (parent of bot/)
    env_path = Path(__file__).parent.parent / ".env.bot.secret"
    
    # Load environment variables from the file
    load_dotenv(env_path)
    
    return {
        "BOT_TOKEN": os.getenv("BOT_TOKEN", ""),
        "LMS_API_URL": os.getenv("LMS_API_URL", ""),
        "LMS_API_KEY": os.getenv("LMS_API_KEY", ""),
        "LLM_API_KEY": os.getenv("LLM_API_KEY", ""),
        "LLM_API_BASE_URL": os.getenv("LLM_API_BASE_URL", ""),
        "LLM_API_MODEL": os.getenv("LLM_API_MODEL", ""),
    }
