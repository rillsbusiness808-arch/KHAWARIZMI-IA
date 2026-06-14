# config.py
# Khawarizmi Pro — Configuration centralisée avec validation

import os
from functools import lru_cache
from typing import List
from pydantic import ConfigDict, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    VERSION: str = "2.0.0"
    app_name: str = "Khawarizmi API"
    environment: str = "development"
    debug: bool = False

    # Sécurité (SECRET_KEY env var mappe sur ce champ)
    secret_key: str = ""
    algorithm: str = "HS256"
    token_expire_min: int = 1440

    # Base de données
    database_url: str = ""

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    cache_ttl: int = 3600

    # IA
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"
    ia_temperature: float = 0.3
    ia_max_tokens: int = 600
    AI_MODEL_PRIMARY: str = "gemini-2.5-flash"

    # Sentry
    SENTRY_DSN: str = ""

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "https://khawarizmi.dz",
        "https://www.khawarizmi.dz",
        "http://localhost:3000"
    ]

    data_dir: str = ""

    # Paiement
    chargily_secret_key: str = ""
    CHARGILY_API_KEY: str = ""
    CHARGILY_SECRET: str = ""

    model_config = ConfigDict(extra='ignore', env_file='.env', env_file_encoding='utf-8')

    @validator("secret_key", pre=True, always=True)
    def validate_secret_key(cls, v):
        if not v:
            raise ValueError(
                "SECRET_KEY non défini. Arrêt du serveur pour sécurité."
            )
        if len(str(v)) < 16:
            raise ValueError(
                "SECRET_KEY trop court. Minimum 16 caractères requis."
            )
        if v == "changeme-use-strong-secret-in-production":
            raise ValueError(
                "SECRET_KEY par défaut interdit en production."
            )
        return v


@lru_cache()
def get_settings() -> Settings:
    return Settings()


def init_sentry():
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        cfg = get_settings()
        if cfg.SENTRY_DSN:
            sentry_sdk.init(dsn=cfg.SENTRY_DSN, integrations=[FastApiIntegration()],
                            traces_sample_rate=0.2, environment=cfg.environment,
                            release=f"khawarizmi-pro@{cfg.VERSION}")
    except ImportError:
        pass

def get_allowed_origins() -> List[str]:
    base_origins = [
        "http://localhost:3000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://127.0.0.1:3000",
        "https://khawarizmi-ia.vercel.app",
        "https://khawarizmi.vercel.app",
        "https://ia-khawarizmi.dz",
        "https://www.ia-khawarizmi.dz",
    ]
    env_value = os.getenv("ALLOWED_ORIGINS", "")
    extra_origins = [
        o.strip()
        for o in env_value.split(",")
        if o.strip() and o.strip().startswith("http")
    ]
    all_origins = list(set(base_origins + extra_origins))
    return all_origins
