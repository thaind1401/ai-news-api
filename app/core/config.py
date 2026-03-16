import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    app_name: str = "ai-signals-api"
    timezone: str = "Asia/Ho_Chi_Minh"
    crawler_interval_minutes: int = 30
    enrichment_retry_interval_minutes: int = 10


def _normalize_value(raw_value: str) -> str:
    value = raw_value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value


def load_dotenv_if_exists(file_path: Path | None = None) -> None:
    path = file_path or (Path(__file__).resolve().parents[2] / ".env")
    if not path.exists() or not path.is_file():
        return

    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        if line.startswith("export "):
            line = line[len("export ") :].strip()

        if "=" not in line:
            continue

        key, raw_value = line.split("=", 1)
        key = key.strip()
        if not key or key in os.environ:
            continue

        os.environ[key] = _normalize_value(raw_value)


def get_app_config() -> AppConfig:
    return AppConfig(
        app_name=os.getenv("APP_NAME", "ai-signals-api"),
        timezone=os.getenv("APP_TIMEZONE", "Asia/Ho_Chi_Minh"),
        crawler_interval_minutes=int(os.getenv("CRAWLER_INTERVAL_MINUTES", "30")),
        enrichment_retry_interval_minutes=int(os.getenv("ENRICHMENT_RETRY_INTERVAL_MINUTES", "10")),
    )
