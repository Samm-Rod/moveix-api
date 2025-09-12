#app/utils/config.py
import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict  # Corrigido para pydantic-settings

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')
REFRESH_SECRET_KEY = os.getenv('REFRESH_KEY', os.getenv('REFRESH_SECRET_KEY', 'default-secret-key'))
ALGORITHM = os.getenv('ALGORITHM', 'HS256')
# Support both ACCESS_tokens_EXPIRE_MINUTES and ACCESS_TOKEN_EXPIRE_MINUTES (typo compat)
ACCESS_tokens_EXPIRE_MINUTES = int(
    os.getenv('ACCESS_tokens_EXPIRE_MINUTES')
    or os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')
    or '30'
)
REFRESH_tokens_EXPIRE_MINUTES = int(os.getenv('REFRESH_tokens_EXPIRE_MINUTES') or os.getenv('REFRESH_TOKEN_EXPIRE_MINUTES') or 60 * 24 * 7)
# Read Google API key commonly named GOOGLE_API_KEY
GOOGLE_MAPS_app_KEY = os.getenv('GOOGLE_API_KEY') or os.getenv('GOOGLE_app_KEY') or 'default-google-maps-app-key'

class Settings(BaseSettings):
    POSTGRES_USER: str = os.getenv('POSTGRES_USER', 'postgres')
    POSTGRES_PASSWORD: str = os.getenv('POSTGRES_PASSWORD', 'postgres')
    POSTGRES_DB: str = os.getenv('POSTGRES_DB', 'moveix_db')
    DB_HOST: str = os.getenv('DB_HOST', 'db')
    DB_PORT: str = os.getenv('DB_PORT', '5432')
    DB_USER: str = os.getenv('DB_USER', 'postgres')
    DB_PASS: str = os.getenv('DB_PASS', 'postgres')
    DB_NAME: str = os.getenv('DB_NAME', 'moveix_db')
    SECRET_KEY: str = SECRET_KEY
    ALGORITHM: str = ALGORITHM
    ACCESS_tokens_EXPIRE_MINUTES: int = ACCESS_tokens_EXPIRE_MINUTES
    MAIL_USERNAME: str = os.getenv('MAIL_USERNAME', '')
    MAIL_PASSWORD: str = os.getenv('MAIL_PASSWORD', '')
    MAIL_FROM: str = os.getenv('MAIL_FROM', '')
    MAIL_PORT: str = os.getenv('MAIL_PORT', '587')
    MAIL_SERVER: str = os.getenv('MAIL_SERVER', '')
    MAIL_FROM_NAME: str = os.getenv('MAIL_FROM_NAME', '')
    MAIL_STARTTLS: str = os.getenv('MAIL_STARTTLS', 'True')
    MAIL_SSL_TLS: str = os.getenv('MAIL_SSL_TLS', 'False')
    GOOGLE_app_KEY: str = GOOGLE_MAPS_app_KEY
    GOOGLE_MAPS_app_KEY: str = GOOGLE_MAPS_app_KEY


    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()


