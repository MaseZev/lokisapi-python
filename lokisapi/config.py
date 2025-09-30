"""
Configuration helpers for LokisApi.
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Settings:
    api_key: str
    base_url: str = "https://lokisapi.online/v1"
    timeout_seconds: int = 30
    retries: int = 2
    backoff_factor: float = 0.5

    @classmethod
    def from_env(cls, prefix: str = "LOKISAPI_") -> "Settings":
        api_key = os.getenv(f"{prefix}API_KEY", "")
        base_url = os.getenv(f"{prefix}BASE_URL", "https://lokisapi.online/v1")
        timeout = int(os.getenv(f"{prefix}TIMEOUT", "30") or 30)
        retries = int(os.getenv(f"{prefix}RETRIES", "2") or 2)
        backoff = float(os.getenv(f"{prefix}BACKOFF", "0.5") or 0.5)
        return cls(api_key=api_key, base_url=base_url, timeout_seconds=timeout, retries=retries, backoff_factor=backoff)


