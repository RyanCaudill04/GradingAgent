from pydantic_settings import BaseSettings
from pydantic import PostgresDsn

class Settings(BaseSettings):
    ENV: str = "development"
    ALLOWED_ORIGINS: list[str] = ["http://localhost:8000", "http://django:8000", "http://127.0.0.1:8000"]

    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_SERVER: str = "db"
    POSTGRES_DB: str = "postgres"
    POSTGRES_PORT: int = 5432

    DATABASE_URL: str | None = None

    @property
    def DATABASE_URL_USED(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        env_file = ".env"

settings = Settings()
