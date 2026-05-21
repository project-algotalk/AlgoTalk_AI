from fastapi import FastAPI
from app.api.v1.interview import router as interview_router
app = FastAPI(title="AlgoTalk AI Service")
app.include_router(interview_router, prefix="/ai/v1/interview")
