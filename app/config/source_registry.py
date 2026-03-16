import json
import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = Path(__file__).with_name("sources.json")


def _ensure_required_fields(item: dict[str, Any], index: int) -> None:
    required = ["name", "base_url", "source_type", "ingest_method", "discovery"]
    missing = [field for field in required if field not in item]
    if missing:
        raise ValueError(f"Invalid source config at index {index}: missing {', '.join(missing)}")


def load_source_registry() -> list[dict[str, Any]]:
    config_path = Path(os.getenv("SOURCES_CONFIG_PATH", str(DEFAULT_CONFIG_PATH))).expanduser()
    if not config_path.exists():
        logger.warning("Sources config file not found: %s", config_path)
        return []

    data = json.loads(config_path.read_text(encoding="utf-8"))
    sources = data.get("sources", [])
    if not isinstance(sources, list):
        raise ValueError("Invalid sources config: 'sources' must be a list")

    validated: list[dict[str, Any]] = []
    for index, item in enumerate(sources):
        if not isinstance(item, dict):
            raise ValueError(f"Invalid source config at index {index}: item must be an object")
        _ensure_required_fields(item, index)
        if item.get("enabled", False):
            validated.append(item)

    return validated