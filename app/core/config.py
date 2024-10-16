from pydantic_settings import BaseSettings, SettingsConfigDict


class ApplicationSettings(BaseSettings):
    APP_NAME: str = "Project Managament API Service"
    APP_DESCRIPTION: str = "Project managamente API backend service."
    APP_VERSION: str = "v1.0.0"
    DEBUG: bool = False
    JWT_SECRET_KEY: str = "your-secret-key"
    JWT_ALGORITHM: str = "HS256"
    DATABASE_URL: str = "sqlite:///./test.db"
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]

    STRIPE_SECRET_KEY: str = "your-stripe-secret-key"
    STRIPE_MONTHLY_PRICE_ID: str = "your-stripe-monthly-price-id"
    STRIPE_ANNUAL_PRICE_ID: str = "your-stripe-annual-price-id"
    STRIPE_SUCCESS_URL: str = "http://localhost:3000/success"
    STRIPE_CANCEL_URL: str = "http://localhost:3000/cancel"

    TEST_DATABASE_URL: str = "sqlite:///:memory:"

    model_config = SettingsConfigDict(env_file=".env")
