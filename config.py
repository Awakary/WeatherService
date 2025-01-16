import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    WEATHER_API_KEY: str

    model_config = SettingsConfigDict(env_file=".env")

    @property
    def DB_URL(self):
        if os.environ.get("PYTEST_VERSION"):
            return "sqlite:///./test_db.db"
        return f'postgresql+psycopg2://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'


settings = Settings()
