from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "PyCommerce"
    debug: bool = False

    database_url: str = "postgresql+asyncpg://admin:admin@localhost:5432/pycommerce"
    jwt_secret: str = "your-secret-key"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")


settings = Settings()
