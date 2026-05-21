from fastapi import APIRouter
from app.schemas.interview import (
    QuestionGenerateRequestDTO,
    QuestionGenerateResponseDTO,
    CsValidationRequestDTO,
    CsValidationResponseDTO,
)
from app.services.interview_service import generate_questions, validate_cs_questions
router = APIRouter()
# 면접 질문 생성 엔드포인트
# interviewService로부터 요청을 받아 LLM 기반 질문 생성 후 반환
@router.post("/questions", response_model=QuestionGenerateResponseDTO)
def create_questions(request: QuestionGenerateRequestDTO) -> QuestionGenerateResponseDTO:
    # 질문 생성 서비스 호출
    return generate_questions(request)
# CS 질문 검증 엔드포인트
# interviewService로부터 직접입력 질문 목록을 받아 CS 관련 여부 판단 후 반환
@router.post("/validate/cs-questions", response_model=CsValidationResponseDTO)
def validate_questions(request: CsValidationRequestDTO) -> CsValidationResponseDTO:
    return validate_cs_questions(request)