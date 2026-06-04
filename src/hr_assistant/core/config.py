from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings for the application."""

    app_name: str = "AI RRHH Chatbot"

    gemini_api_key: str
    gemini_model: str
    gemini_embedding_model: str

    postgres_dsn: str

    postgres_user: str
    postgres_password: str
    postgres_db: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()