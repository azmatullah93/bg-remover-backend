from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MAX_FILE_SIZE_MB: int = 8
    RATE_LIMIT_PER_MINUTE: int = 10
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    CORS_ORIGINS: str | None = None
    MODEL_NAME: str = "u2net"
    REQUEST_TIMEOUT_SECONDS: int = 60

    @property
    def max_upload_size_bytes(self) -> int:
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

    @property
    def allowed_origins_list(self) -> list[str]:
        origins = (self.CORS_ORIGINS or self.ALLOWED_ORIGINS).strip()
        return [o.strip() for o in origins.split(",") if o.strip()]

    class Config:
        env_file = ".env"
        extra = "ignore"


config = Settings()
