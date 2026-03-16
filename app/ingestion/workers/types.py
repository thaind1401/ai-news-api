from dataclasses import dataclass, field
from typing import Any


@dataclass
class SourceIngestionResult:
    source_name: str
    links_discovered: int = 0
    raw_items_created: int = 0
    signals_created: int = 0
    duplicates_skipped: int = 0
    crawl_errors: int = 0
    saved_items: list[dict[str, Any]] = field(default_factory=list)
