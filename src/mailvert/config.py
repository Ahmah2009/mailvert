from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MAILVERT_", env_file=".env", extra="ignore")

    # Identity used for the SMTP MAIL FROM / EHLO handshake.
    smtp_from_address: str = "verify@mailvert.local"
    smtp_helo_host: str = "mailvert.local"

    # Network behaviour.
    smtp_timeout_seconds: float = 8.0
    dns_timeout_seconds: float = 5.0
    max_mx_hosts_tried: int = 2

    # Whether to attempt a live SMTP RCPT TO handshake at all. Many networks
    # (most cloud providers) block outbound port 25, in which case this
    # should be disabled and verification falls back to syntax + MX only.
    smtp_probe_enabled: bool = True

    # Result caching.
    cache_ttl_seconds: int = 60 * 30
    cache_max_size: int = 10_000

    # API behaviour.
    rate_limit: str = "30/minute"
    cors_origins: list[str] = ["*"]
    bulk_max_addresses: int = 50
    bulk_concurrency: int = 10

    log_level: str = "INFO"
    log_json: bool = False


settings = Settings()
