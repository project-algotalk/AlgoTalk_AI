# %%
from fastapi import FastAPI
from app.api.v1.interview import router as interview_router
from app.api.v1.validation import router as validation_router
from app.api.v1.stt import router as stt_router
app = FastAPI(title="AlgoTalk AI Service")
app.include_router(interview_router, prefix="/ai/v1/interview")
app.include_router(validation_router, prefix="/ai/v1/validate")
app.include_router(stt_router, prefix="/ai/v1/stt")