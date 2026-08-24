import json
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    app_env: str = "development"
    debug: bool = False  # Override via DEBUG=true env var
    log_level: str = "INFO"
    log_format: str = "console"  # console | json

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/openskill"
    db_pool_size: int = 5
    db_max_overflow: int = 10

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # S3 / MinIO
    s3_endpoint: str = "http://localhost:9000"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    s3_bucket: str = "openskill"
    s3_region: str = "us-east-1"

    # Auth / JWT
    jwt_secret: str = "dev-secret-change-me-in-production"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    # Concurrent-refresh grace: a just-rotated token re-presented within this
    # window is a cross-tab race (shared cookie, per-tab dedup), not theft —
    # the loser tab gets its own fresh pair instead of a forced logout.
    refresh_reuse_grace_seconds: int = 10

    # LLM
    llm_provider: str = "anthropic"  # anthropic | openai
    llm_model: str = "claude-sonnet-5"
    anthropic_api_key: str = ""
    openai_api_key: str = ""

    # Evaluation
    eval_max_concurrent: int = 10
    eval_timeout_seconds: int = 120
    eval_max_video_frames: int = 8
    eval_max_video_duration: int = 600  # seconds
    eval_max_image_size: int = 20 * 1024 * 1024  # 20 MB
    eval_max_retries: int = 3

    # Workflow runtime (Issue #21)
    credential_encryption_key: str = ""  # Fernet key or passphrase; required in production
    extraction_enabled: bool = False  # LLM requirement extraction feature flag
    workflow_step_timeout_seconds: int = 120
    workflow_max_concurrent_runs: int = 20

    # Frontend
    frontend_url: str = "http://localhost:3000"

    # CORS
    cors_origins: list[str] = ["http://localhost:3000"]

    # API
    api_prefix: str = "/api/v1"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors(cls, v: object) -> object:
        if isinstance(v, str):
            return json.loads(v)
        return v

    @field_validator("jwt_secret")
    @classmethod
    def validate_jwt_secret(cls, v: str, info: Any) -> str:
        # Read app_env from the pydantic model field, not os.environ.
        # pydantic-settings loads .env values into model fields but does NOT
        # propagate them to os.environ, so os.environ.get("APP_ENV") can
        # return None even when APP_ENV=production is set in .env.
        app_env = (info.data.get("app_env") or "development") if info.data else "development"
        if (
            app_env not in ("development", "test")
            and v == "dev-secret-change-me-in-production"
        ):
            raise ValueError("JWT_SECRET must be set to a unique value in production")
        return v

    @field_validator("s3_secret_key")
    @classmethod
    def validate_s3_secret(cls, v: str, info: Any) -> str:
        app_env = (info.data.get("app_env") or "development") if info.data else "development"
        if app_env not in ("development", "test") and v == "minioadmin":
            raise ValueError("S3_SECRET_KEY must be changed from default in production")
        return v

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str, info: Any) -> str:
        app_env = (info.data.get("app_env") or "development") if info.data else "development"
        if app_env not in ("development", "test") and "postgres:postgres@" in v:
            raise ValueError("DATABASE_URL must not use default postgres:postgres credentials in production")
        return v

    @field_validator("credential_encryption_key")
    @classmethod
    def validate_credential_key(cls, v: str, info: Any) -> str:
        app_env = (info.data.get("app_env") or "development") if info.data else "development"
        if app_env not in ("development", "test") and not v:
            raise ValueError("CREDENTIAL_ENCRYPTION_KEY must be set in production")
        return v

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


settings = Settings()
