from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .job import TranslationServer
import uvicorn


class JobID(BaseModel):
    job_id: str


class JobResponse(BaseModel):
    response: str


class TranslationAPI:
    def __init__(self):
        self.app = FastAPI(title="Video Translation Server")
        self.translation_server = TranslationServer()
        self.setup_routes()

    def setup_routes(self):
        self.app.post("/jobs")(self.create_translation_job)
        self.app.get("/status/{job_id}")(self.get_translation_status)

    async def create_translation_job(
        self, processing_time: float = 10.0, error_probability: float = 0.1
    ) -> JobID:
        if processing_time <= 0:
            raise HTTPException(
                status_code=400, message="Processing time must be positive"
            )
        if not 0 <= error_probability <= 1:
            raise HTTPException(
                status_code=400, message="Error probability must be between 0 and 1"
            )

        job_id = self.translation_server.create_job(
            processing_time=processing_time, error_probability=error_probability
        )
        return JobID(job_id=job_id)

    async def get_translation_status(self, job_id: str) -> JobResponse:
        status = self.translation_server.get_job_status(job_id)
        if status is None:
            raise HTTPException(status_code=404, detail="Job Not Found")
        return JobResponse(response=status.value)

    def run(self, host: str = "0.0.0.0", port: int = 8000):
        uvicorn.run(self.app, host=host, port=port)
