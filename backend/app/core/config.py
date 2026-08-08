import os
from dotenv import load_dotenv

load_dotenv()


class Setting:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    MONGODB_URL_KEY: str = os.getenv("MONGODB_URL_KEY", "")

    DEFAULT_MODELS: list[str] = [
        "deepseek/deepseek-chat",
        "groq/llama-3.3-70b-versatile",
    ]
    MAX_RETRIES: int = 3
    RETRY_DELAY: float = 1.0


Setting.setting = Setting
