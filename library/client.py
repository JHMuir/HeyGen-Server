from typing import Optional, Callable, Any
from enum import Enum
import httpx
import logging
import time

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class TranslationStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    ERROR = "error"


class CircuitBreakerError(Exception):
    pass


class TranslationClient:
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        initial_retry_delay: float = 1.0,
        max_retry_delay: float = 60.0,
        backoff_factor: float = 2.0,
        max_retries: int = 10,
        timeout: float = 5.0,
        circuit_breaker_threshold: int = 5,
        circuit_breaker_timeout: float = 60.0,
    ):
        self.base_url = base_url
        self.initial_retry_delay = initial_retry_delay
        self.max_retry_delay = max_retry_delay
        self.backoff_factor = backoff_factor
        self.max_retries = max_retries
        self.timeout = timeout
        self.circuit_breaker_threshold = circuit_breaker_threshold
        self.circuit_breaker_timeout = circuit_breaker_timeout
        self.logger = logging.getLogger(__name__)
        self._consecutive_failures = 0
        self._circuit_broken_time: Optional[float] = None
        self._http_client = httpx.Client(timeout=self.timeout)

    def create_job(self, processing_time: float = 30.0, error_probability: float = 0.1):
        self._check_circuit_breaker()

        try:
            response = self._http_client.post(
                f"{self.base_url}/jobs",
                params={
                    "processing_time": processing_time,
                    "error_probability": error_probability,
                },
            )
            response.raise_for_status()
            self._consecutive_failures = 0  # Reset on success
            return response.json()["job_id"]
        except Exception as e:
            self._handle_request_error(e)

    def get_status(self, job_id: str):
        try:
            response = self._http_client.get(f"{self.base_url}/status/{job_id}")
            response.raise_for_status()
            self._consecutive_failures = 0  # Reset on success
            return TranslationStatus(response.json()["result"])
        except Exception as e:
            self._handle_request_error(e)

    def wait_for_completion(
        self, job_id: str, callback: Optional[Callable[[TranslationStatus], Any]] = None
    ) -> TranslationStatus:
        delay = self.initial_retry_delay
        attempt = 0

        while True:
            status = self.get_status(job_id)
            if callback:
                callback(status)

            if not self._should_retry(status, attempt):
                return status

            time.sleep(delay)
            delay = min(delay * self.backoff_factor, self.max_retry_delay)
            attempt += 1

    def wait_for_completion_with_interval(
        self,
        job_id: str,
        interval: float,
        callback: Optional[Callable[[TranslationStatus], Any]] = None,
    ) -> TranslationStatus:
        if interval <= 0:
            raise ValueError("Interval must be greater than 0")

        while True:
            status = self.get_status(job_id)
            if callback:
                callback(status)

            if status != TranslationStatus.PENDING:
                return status

            time.sleep(interval)

    def _check_circuit_breaker(self):
        """Check if circuit breaker is tripped and if it can be reset"""
        if self._circuit_broken_time is None:
            return

        if time.time() - self._circuit_broken_time >= self.circuit_breaker_timeout:
            self.logger.info("Resetting circuit breaker")
            self._consecutive_failures = 0
            self._circuit_broken_time = None
            return

        raise CircuitBreakerError("Circuit breaker is open")

    def _handle_request_error(self, e: Exception):
        """Handle request errors and manage circuit breaker state"""
        self._consecutive_failures += 1
        if self._consecutive_failures >= self.circuit_breaker_threshold:
            self._circuit_broken_time = time.time()
            raise CircuitBreakerError("Circuit breaker tripped") from e
        raise e

    def _should_retry(self, status: TranslationStatus, attempt: int) -> bool:
        """Determine if we should retry based on status and attempt count"""
        if attempt >= self.max_retries:
            return False
        return status == TranslationStatus.PENDING

    def __enter__(self):
        """Context manager support"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensure client is properly closed"""
        self._http_client.close()
