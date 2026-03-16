import os
import secrets
from typing import Optional


def read_internal_api_key() -> str:
    return os.getenv("INTERNAL_API_KEY", "").strip()


def is_valid_internal_key(candidate: Optional[str], expected: str) -> bool:
    if not candidate or not expected:
        return False
    return secrets.compare_digest(candidate, expected)
