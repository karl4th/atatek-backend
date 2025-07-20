from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    HOST: str = os.getenv('DB_HOST', 'localhost')
    PORT: int = int(os.getenv('DB_PORT', '5432')) if os.getenv('DB_PORT', '5432').isdigit() else 5432
    USER: str = os.getenv('DB_USER', 'atatek_admin')
    PASSWORD: str = os.getenv('DB_PASSWORD', 'atatek_admin')
    BASE: str = os.getenv('DB_NAME', 'atatek_admin')

    JWT_SECRET_KEY: str = os.getenv('JWT_SECRET_KEY', 'secret')

    @property
    def get_base_link(self):
        return f"postgresql+asyncpg://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.BASE}"
    
    @property
    def get_base_link_for_alembic(self):
        return f"postgresql+asyncpg://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.BASE}?async_fallback=true"
    
    @property
    def get_jwt_secret_key(self):
        return self.JWT_SECRET_KEY
    

settings = Settings()
    
