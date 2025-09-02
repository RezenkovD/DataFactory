from __future__ import annotations

import os

from pydantic import BaseModel


class Settings(BaseModel):
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", "3306"))
    db_name: str = os.getenv("DB_NAME", "datafactory")
    db_user: str = os.getenv("DB_USER", "app")
    db_password: str = os.getenv("DB_PASSWORD", "app")
    api_key: str = os.getenv("API_KEY", "dev-secret-key")
    seed_on_startup: bool = os.getenv("SEED_ON_STARTUP", "false").lower() == "true"

    @property
    def sqlalchemy_url(self) -> str:
        return (
            f"mysql+aiomysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


settings = Settings()
