from enum import Enum
import time
import random
from typing import Dict, Optional
import logging
import uuid

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class JobStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    ERROR = "error"


class TranslationJob:
    def __init__(self, processing_time: float, error_probability: float = 0.1):
        self.job_id = str(uuid.uuid4())
        self.start_time = time.time()
        self.processing_time = processing_time
        self.error_probability = error_probability

    def get_status(self) -> JobStatus:
        # Comparing the processing time to the actual time worked
        time_worked = time.time() - self.start_time
        # logger.info(f"Time Worked: {time_worked}, Processing Time: {self.processing_time}")
        if time_worked >= self.processing_time:
            logger.info(f"Job status returned: {JobStatus.COMPLETED}")
            return JobStatus.COMPLETED

        # Randomly causing an error if inside error threshold
        error = random.random()
        # logger.info(f"Error: {error}, Threshold:{self.error_probability}")
        if error < self.error_probability:
            logger.info(f"Job status returned: {JobStatus.ERROR}")
            return JobStatus.ERROR
        # If not completed or errored, return pending
        return JobStatus.PENDING


class TranslationServer:
    def __init__(self):
        # dictionary of {str(uuid):TranslationJob}
        self.jobs: Dict[str, TranslationJob] = {}

    def create_job(self, processing_time: float, error_probability: float = 0.1) -> str:
        # Updating our jobs dictionary with a new job
        job = TranslationJob(processing_time, error_probability)
        self.jobs[job.job_id] = job
        logger.info(f"Created TranslationJob, ID:{job.job_id}")
        return job.job_id

    def get_job_status(self, job_id: str) -> Optional[JobStatus]:
        # Grabbing passed job's status
        job = self.jobs.get(job_id)
        if job is None:
            return None
        return job.get_status()
