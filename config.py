import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    PAGE_SIZE: int
    WEATHER_API_KEY: str
    REDIS_PASSWORD: str

    model_config = SettingsConfigDict(env_file=".env")

    @property
    def DB_URL(self):
        if os.environ.get("PYTEST_VERSION"):
            return "sqlite:///./test_db.db"
        return (f'postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:'
                f'{self.POSTGRES_PORT}/{self.POSTGRES_DB}')


settings = Settings()
