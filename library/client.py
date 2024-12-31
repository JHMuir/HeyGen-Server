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
    """
    Raised when circuit breaker is open
    """

    pass


class TranslationClient:
    """Main client for interfacing with the server"""

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
        """
        Initialization with optional parametes

        Args:
            base_url (str, optional): URL to interact with the server. Defaults to "http://localhost:8000".
            initial_retry_delay (float, optional): Initial delay between retries, in seconds. Defaults to 1.0.
            max_retry_delay (float, optional): Maximum delay between retries, in seconds. Defaults to 60.0.
            backoff_factor (float, optional): Multiplier for exponential backoff. Defaults to 2.0.
            max_retries (int, optional): Maximum number of consecutive retries. Defaults to 10.
            timeout (float, optional): Timeout for each HTTP request, in seconds. Defaults to 5.0.
            circuit_breaker_threshold (int, optional): Number of failures before circuit breaks. Defaults to 5.
            circuit_breaker_timeout (float, optional): Time to wait before resetting circuit, in seconds. Defaults to 60.0.
        """
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
        """
        Creates a new job

        Args:
            processing_time (float, optional): Expected processing time, in seconds. Defaults to 30.0.
            error_probability (float, optional): Probability of job failing. Defaults to 0.1.

        Returns:
            job_id (str): uuid4 string, generated for the job

        Raises:
            CircuitBreakerError: If circuit breaker is open
            httpx.HTTPError: For HTTP-related errors
        """
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
        """
        Gets the current status of the job

        Args:
            job_id (str): uuid4 string

        Raises:
            CircuitBreakerError: If circuit breaker is open
            httpx.HTTPError: For HTTP-related errors

        Returns:
            TranslationStatus (Enum): COMPLETED or ERROR or PENDING
        """
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
        """
        Waits for job completion using exponential backoff

        Args:
            job_id (str): uuid4 string
            callback (Optional[Callable[[TranslationStatus], Any]], optional): Optional callback function called on check. Defaults to None.

        Raises:
            CircuitBreakerError: If circuit breaker is open
            httpx.HTTPError: For HTTP-related errors

        Returns:
            TranslationStatus (enum): COMPLETED or ERROR
        """
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
        """
        Waits for job completion on a fixed interval

        Args:
            job_id (str): uuid4 string
            interval (float): Time between checks, in seconds
            callback (Optional[Callable[[TranslationStatus], Any]], optional):  Optional callback function called on check. Defaults to None.

        Raises:
            CircuitBreakerError: If circuit breaker is open
            httpx.HTTPError: For HTTP-related errors
            ValueError: If interval is less than or equal to 0

        Returns:
            TranslationStatus (enum): COMPLETED or ERROR
        """
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
        """
        Check if circuit breaker is tripped and if it can be reset

        Raises:
            CircuitBreakerError: If circuit breaker is open
        """
        if self._circuit_broken_time is None:
            return

        if time.time() - self._circuit_broken_time >= self.circuit_breaker_timeout:
            self.logger.info("Resetting circuit breaker")
            self._consecutive_failures = 0
            self._circuit_broken_time = None
            return

        raise CircuitBreakerError("Circuit breaker is open")

    def _handle_request_error(self, e: Exception):
        """
        Handle request errors and manage circuit breaker state

        Args:
            e (Exception): Exception that occured

        Raises:
            CircuitBreakerError: If circuit breaker is open
            e: Exception that occured
        """
        self._consecutive_failures += 1
        if self._consecutive_failures >= self.circuit_breaker_threshold:
            self._circuit_broken_time = time.time()
            raise CircuitBreakerError("Circuit breaker tripped") from e
        raise e

    def _should_retry(self, status: TranslationStatus, attempt: int) -> bool:
        """
        Determine if we should retry based on status and attempt count

        Args:
            status (TranslationStatus): Current status of the job
            attempt (int): Current number of attempts

        Returns:
            bool: True if the attempt should be retried, False if not
        """
        if attempt >= self.max_retries:
            return False
        return status == TranslationStatus.PENDING

    def __enter__(self):
        """
        Context manager support
        """
        return self

    def __exit__(self):
        """
        Ensure client is properly closed
        """
        self._http_client.close()
