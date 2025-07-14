from pydantic_settings import BaseSettings
from urllib.parse import quote_plus

class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DB_HOST: str
    DB_PORT: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    @property
    def database_url(self) -> str:
        user = quote_plus(self.POSTGRES_USER)
        password = quote_plus(self.POSTGRES_PASSWORD)
        host = self.DB_HOST
        port = self.DB_PORT
        db = self.POSTGRES_DB

        return f"postgresql://{user}:{password}@{host}:{port}/{db}"
    class Config:
        env_file = ".env"

settings = Settings()
