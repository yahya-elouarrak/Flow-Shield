import os


class Settings:
    VULNERABLE_MODE: bool = os.environ.get("VULNERABLE_MODE", "true").lower() == "true"
    JWT_SECRET: str = os.environ.get("JWT_SECRET", "minisub-dev-secret-key-change-in-prod")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60


settings = Settings()
