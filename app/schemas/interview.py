# # 필요한 라이브러리 불러오기
from pydantic import BaseModel
from typing import List
from enum import Enum

# # 함수 설정
# ## 면접 질문 난이도 설정
class Difficulty(str, Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"

# ## 면접 질문 생성 요청 DTO
# interviewService로부터 전달받는 요청 데이터
class QuestionGenerateRequestDTO(BaseModel):
    categories: List[str] # 카테고리 목록 (예: ["백엔드 개발자", "운영체제", "네트워크"])
    questionCount: int    # 생성할 질문 수

class QuestionItemDTO(BaseModel):
    order: int           # 질문 순서 (1부터 시작)
    category: str        # 해당 카테고리명
    difficulty: Difficulty  # 난이도
    content: str         # 질문 내용
    intent: str          # 출제 의도
    keywords: List[str]  # 핵심 키워드 리스트

# ## 면접 질문 생성 응답 DTO
# interviewService로 반환하는 응답 데이터
class QuestionGenerateResponseDTO(BaseModel):
    questions: List[QuestionItemDTO]  # 생성된 질문 목록