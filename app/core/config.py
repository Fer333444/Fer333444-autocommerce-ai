
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "AutoCommerce AI"
    environment: str = "development"
    database_url: str | None = None

    class Config:
        env_file = ".env"


settings = Settings()
