from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .job import TranslationServer
import uvicorn


class JobID(BaseModel):
    job_id: str


class JobResult(BaseModel):
    result: str


class TranslationAPI:
    """
    Server API that interacts with backend
    """

    def __init__(self):
        """
        Initialization of the API
        """
        self.app = FastAPI(title="Video Translation Server")
        self.translation_server = TranslationServer()
        self.setup_routes()

    def setup_routes(self):
        """
        Initialization of POST and GET routes
        """
        self.app.post("/jobs")(self.create_translation_job)
        self.app.get("/status/{job_id}")(self.get_translation_status)

    async def create_translation_job(
        self, processing_time: float = 30.0, error_probability: float = 0.1
    ) -> JobID:
        """
        Creates a new job

        Args:
            processing_time (float, optional): Expected processing time, in seconds. Defaults to 30.0.
            error_probability (float, optional): Probability of job failing. Defaults to 0.1.

        Raises:
            HTTPException: For HTTP-related errors

        Returns:
            JobID: Pydantic model that contains the generated uuid4 string
        """
        if processing_time <= 0:
            raise HTTPException(
                status_code=400, detail="Processing time must be positive"
            )
        if not 0 <= error_probability <= 1:
            raise HTTPException(
                status_code=400, detail="Error probability must be between 0 and 1"
            )

        job_id = self.translation_server.create_job(
            processing_time=processing_time, error_probability=error_probability
        )
        return JobID(job_id=job_id)

    async def get_translation_status(self, job_id: str) -> JobResult:
        """
        Retrieves the current status of the job

        Args:
            job_id (str): uuid4 string

        Raises:
            HTTPException: For HTTP-related errors

        Returns:
            JobResult: Pydantic model that contains the response string
        """
        status = self.translation_server.get_job_status(job_id)
        if status is None:
            raise HTTPException(status_code=404, detail="Job Not Found")
        return JobResult(result=status.value)

    def run(self, host: str = "0.0.0.0", port: int = 8000):
        uvicorn.run(self.app, host=host, port=port)
