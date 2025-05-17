import os
from dotenv import load_dotenv


load_dotenv()

class Settings:
    API_URL_SERVER = os.getenv("API_URL_SERVER")
    AGENT_NAME = os.getenv("AGENT_NAME", "Agente GPT")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

settings = Settings()
