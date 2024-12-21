from enum import Enum
import time
import random
from typing import Dict, Optional
import uuid


class JobStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    ERROR = "error"


class TranslationJob:
    def __init__(self, processing_time: float, error_threshold: float = 0.1):
        self.job_id = str(uuid.uuid4())
        self.start_time = time.time()
        self.processing_time = processing_time
        self.error_threshold = error_threshold

    def get_status(self) -> JobStatus:
        # Randomly causing an error if inside error threshold
        error = random.random()
        print(f"Error: {error}, Threshold:{self.error_threshold}")
        if error < self.error_threshold:
            print(JobStatus.ERROR)
            return JobStatus.ERROR

        # Comparing the processing time to the actual time worked
        time_worked = time.time() - self.start_time
        print(f"Time Worked: {time_worked}, Processing Time: {self.processing_time}")
        if time_worked >= self.processing_time:
            print(JobStatus.COMPLETED)
            return JobStatus.COMPLETED
        else:
            print(JobStatus.PENDING)
            return JobStatus.PENDING


class TranslationJobs:
    def __init__(self):
        # dictionary of {str(uuid):TranslationJob}
        self.jobs: Dict[str, TranslationJob] = {}

    def create_job(self, processing_time: float, error_threshold: float = 0.1) -> str:
        # Updating our jobs dictionary with a new job
        job = TranslationJob(processing_time, error_threshold)
        self.jobs[job.job_id] = job
        return job.job_id

    def get_job_status(self, job_id: str) -> Optional[JobStatus]:
        # Grabbing passed job's status
        job = self.jobs.get(job_id)
        if job is None:
            return None
        return job.get_status()
