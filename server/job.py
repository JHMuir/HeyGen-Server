from enum import Enum
import time
import random


class JobStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    ERROR = "error"


class TranslationJob:
    def __init__(self, processing_time: float, error_threshold: float = 0.1):
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


class TranslationJobServer:
    pass
