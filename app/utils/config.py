import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict  # Corrigido para pydantic-settings

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')
ALGORITHM = os.getenv('ALGORITHM','HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '1440'))
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_API_KEY', 'default-google-maps-api-key')

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
    ACCESS_TOKEN_EXPIRE_MINUTES: int = ACCESS_TOKEN_EXPIRE_MINUTES
    MAIL_USERNAME: str = os.getenv('MAIL_USERNAME', '')
    MAIL_PASSWORD: str = os.getenv('MAIL_PASSWORD', '')
    MAIL_FROM: str = os.getenv('MAIL_FROM', '')
    MAIL_PORT: str = os.getenv('MAIL_PORT', '587')
    MAIL_SERVER: str = os.getenv('MAIL_SERVER', '')
    MAIL_FROM_NAME: str = os.getenv('MAIL_FROM_NAME', '')
    MAIL_STARTTLS: str = os.getenv('MAIL_STARTTLS', 'True')
    MAIL_SSL_TLS: str = os.getenv('MAIL_SSL_TLS', 'False')
    GOOGLE_API_KEY: str = GOOGLE_MAPS_API_KEY
    GOOGLE_MAPS_API_KEY: str = GOOGLE_MAPS_API_KEY


    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()


