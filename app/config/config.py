import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    API_URL_SERVER = os.getenv("API_URL_SERVER", "http://127.0.0.1:8080/api")
    AGENT_NAME = os.getenv("AGENT_NAME", "Asistente ProjectJ")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


settings = Settings()
