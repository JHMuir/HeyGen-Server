from dataclasses import dataclass
from enum import Enum


@dataclass
class TranslationConfig:
    base_url: str = "http://localhost:8000"
    initial_retry_delay: float = 1.0
    max_retry_delay: float = 60.0
    backoff_factor: float = 2.0
    max_retries: int = 10
    timeout: float = 5.0
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: float = 60.0


class TranslationStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    ERROR = "error"


class CircuitBreakerError(Exception):
    pass
