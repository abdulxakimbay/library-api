# Third party
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SECRET_KEY: str
    DB_LINK: str
    TEST_DB_LINK: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 3

    @property
    def get_secret_key(self):
        return self.SECRET_KEY

    @property
    def get_db_url(self):
        return self.DB_LINK

    @property
    def get_test_db_url(self):
        return self.TEST_DB_LINK

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
