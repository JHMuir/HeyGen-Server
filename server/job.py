from enum import Enum
import time
import random
from typing import Dict, Optional
import logging
import uuid

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class JobStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    ERROR = "error"


class TranslationJob:
    """
    Basic job object
    """

    def __init__(self, processing_time: float, error_probability: float):
        """
        Initialization of TranslationJob

        Args:
            processing_time (float): Expected processing time, in seconds.
            error_probability (float, optional): Probability of job failing.
        """
        self.job_id = str(uuid.uuid4())
        self.start_time = time.time()
        self.processing_time = processing_time
        self.error_probability = error_probability
        self.logger = logging.getLogger(__name__)

    def get_status(self) -> JobStatus:
        """
        Retrieves current status of the job

        Returns:
            JobStatus (Enum): COMPLETED or PENDING or ERROR
        """
        # Comparing the processing time to the actual time worked
        time_worked = time.time() - self.start_time
        # logger.info(f"Time Worked: {time_worked}, Processing Time: {self.processing_time}")
        if time_worked >= self.processing_time:
            self.logger.info(f"Job status returned: {JobStatus.COMPLETED}")
            return JobStatus.COMPLETED

        # Randomly causing an error if inside error probability
        error = random.random()
        # logger.info(f"Error: {error}, Probability:{self.error_probability}")
        if error < self.error_probability:
            self.logger.info(f"Job status returned: {JobStatus.ERROR}")
            return JobStatus.ERROR
        # If not completed or errored, return pending
        return JobStatus.PENDING


class TranslationServer:
    """
    Backend archtecture that handles multiple TranslationJobs
    """

    def __init__(self):
        """
        Initialization of TranslationServer
        """
        # dictionary of {str(uuid):TranslationJob}
        self.jobs: Dict[str, TranslationJob] = {}
        self.logger = logging.getLogger(__name__)

    def create_job(self, processing_time: float, error_probability: float) -> str:
        """
        Creates a new job

        Args:
            processing_time (float): Expected processing time, in seconds.
            error_probability (float, optional): Probability of job failing.

        Returns:
            job.job_id (str): Returns uuid4 string of created TranslationJob
        """
        # Updating our jobs dictionary with a new job
        job = TranslationJob(processing_time, error_probability)
        self.jobs[job.job_id] = job
        self.logger.info(f"Created TranslationJob, ID:{job.job_id}")
        return job.job_id

    def get_job_status(self, job_id: str) -> Optional[JobStatus]:
        """
        Retrieves job status

        Args:
            job_id (str): uuid4 string

        Returns:
            Optional[JobStatus]: Returns COMPLETED or PENDING or ERROR, or None if job is not found
        """
        # Grabbing passed job's status
        job = self.jobs.get(job_id)
        if job is None:
            return None
        return job.get_status()
