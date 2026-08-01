from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DB_HOST: str
    DB_PORT: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Origens permitidas para o frontend consumir a API (CORS).
    # Ex no .env: CORS_ORIGINS=http://localhost:5173,https://app.seudominio.com
    CORS_ORIGINS_RAW: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    @property
    def CORS_ORIGINS(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS_RAW.split(",") if origin.strip()]

    @property
    def database_url(self) -> str:
        user = quote_plus(self.POSTGRES_USER)
        password = quote_plus(self.POSTGRES_PASSWORD)

        return f"postgresql://{user}:{password}" f"@{self.DB_HOST}:{self.DB_PORT}/{self.POSTGRES_DB}"


settings = Settings()
