# %%
from typing import Annotated

from fastapi import APIRouter, UploadFile, File, Form
from app.schemas.stt import SttResponseDTO
from app.services.stt_service import transcribe_audio
# %%
router = APIRouter()
# %%
# STT 음성 변환 엔드포인트
# interviewService로부터 음성 파일을 받아 텍스트 변환 및 분석 지표 반환
@router.post("/transcribe", response_model=SttResponseDTO)
async def transcribe(
    file: UploadFile = File(...),
    question_text: Annotated[str | None, Form(alias="questionText")] = None,
) -> SttResponseDTO:
    return transcribe_audio(file, question_text=question_text)
# %%
