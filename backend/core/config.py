from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DEBUG: bool = False
    DATABASE_URL: str
    TEST_DATABASE_URL: str
    SECRET_KEY: str

    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_STARTTLS: bool
    MAIL_SSL_TLS: bool

    RABBITMQ_URL: str
    RABBITMQ_EMAIL_QUEUE: str = "email.order_confirmation"
    RABBITMQ_EMAIL_EXCHANGE: str = "email.exchange"
    RABBITMQ_RETRY_EXCHANGE: str = "email.retry.exchange"
    RABBITMQ_DLQ_EXCHANGE: str = "email.dlq.exchange"
    RABBITMQ_RETRY_QUEUE: str = "email.order_confirmation.retry"
    RABBITMQ_DLQ_QUEUE: str = "email.order_confirmation.dlq"
    RABBITMQ_RETRY_DELAY_SECONDS: int = 30
    RABBITMQ_MAX_RETRIES: int = 5

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
