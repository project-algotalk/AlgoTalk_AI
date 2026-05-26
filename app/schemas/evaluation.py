from pydantic import BaseModel, Field
from typing import Annotated

# 답변 평가 요청 DTO
class AnswerEvaluationRequestDTO(BaseModel):
    questionText: str                          # 질문 텍스트
    keywords: list[str] = Field(default_factory=list)  # 핵심 키워드 목록
    answerText: str                            # 사용자 답변 텍스트

# 답변에 대한 구체적인 피드백 DTO
class FeedbackDTO(BaseModel):
    good: str        # 잘한 점
    improve: str     # 부족한 점 및 개선 방향
    addition: str    # 추가하면 좋을 내용

# 답변 평가 응답 DTO
class AnswerEvaluationResponseDTO(BaseModel):
    contentScore: Annotated[int, Field(ge=0, le=25)] # 답변 논리정 점수, 0~25
    feedback: FeedbackDTO   # 구조화된 피드백
    modelAnswer: str        # 모범 답안
    studyTip: str           # 학습 Tip
    followUpQuestions: list[str] = Field(default_factory=list) # 꼬리 질문 예상 목록