from fastapi import APIRouter
from app.schemas.evaluation import (
    AnswerEvaluationRequestDTO,
    AnswerEvaluationResponseDTO,
)
from app.services.evaluation_service import evaluate_answer

router = APIRouter()

# 답변 내용 평가 엔드포인트
# interviewService로부터 질문, 키워드, 답변을 받아
# LLM 기반 점수, 피드백, 모범 답변 반환
@router.post("/evaluate", response_model=AnswerEvaluationResponseDTO)
def evaluate_answer_api(request: AnswerEvaluationRequestDTO) -> AnswerEvaluationResponseDTO:
    return evaluate_answer(request)