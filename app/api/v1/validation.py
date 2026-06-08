from fastapi import APIRouter
from app.schemas.interview import (
    CsValidationRequestDTO,
    CsValidationResponseDTO,
)
from app.services.interview_service import validate_cs_questions
router = APIRouter()
# CS 질문 검증 엔드포인트
# interviewService로부터 직접입력 질문 목록을 받아 CS 관련 여부 판단 후 반환
@router.post("/cs-questions", response_model=CsValidationResponseDTO)
def validate_questions(request: CsValidationRequestDTO) -> CsValidationResponseDTO:
    return validate_cs_questions(request)
