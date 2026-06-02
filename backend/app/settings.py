from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://taskuser:taskpass@localhost:5432/taskdb"
    secret_key: str = "dev-secret-key-change-in-production-12345"
    log_level: str = "INFO"
    cors_origins: list[str] = [
        "http://localhost",
        "http://localhost:80",
        "http://localhost:4200",
    ]
    access_token_expire_minutes: int = 1440

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
