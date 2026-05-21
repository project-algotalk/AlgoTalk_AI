from fastapi import HTTPException
from openai import OpenAI
import logging
from app.schemas.interview import (
    QuestionGenerateRequestDTO,   # 질문 생성 요청 DTO
    QuestionGenerateResponseDTO,  # 질문 생성 응답 DTO
)
# 설정 모듈에서 환경변수 로드
from app.core.config import settings
logger = logging.getLogger(__name__)
# OpenAI 클라이언트 초기화
client = OpenAI(api_key=settings.OPENAI_API_KEY)
def generate_questions(request: QuestionGenerateRequestDTO) -> QuestionGenerateResponseDTO:
    """
    LLM 기반 면접 질문 생성 함수
    interviewService로부터 카테고리, 질문 수를 받아
    OpenAI Structured Output으로 정형화된 질문 목록 반환
    """

    # 카테고리 리스트를 문자열로 변환 (프롬프트 삽입용)
    categories_str = ", ".join(request.categories)

    # LLM 질문 생성 프롬프트 구성
    prompt = f"""
당신은 CS 기술면접 전문가입니다.
아래 조건에 맞는 면접 질문을 생성해주세요.
모든 질문과 답변은 반드시 한국어로 작성하세요.

- 카테고리: {categories_str}
- 질문 수: {request.questionCount}개

각 질문은 반드시 다음 형식으로 작성하세요:
- order: 질문 순서 (1부터 시작)
- category: 해당 카테고리명 (위 카테고리 중 하나)
- difficulty: 난이도 (반드시 대문자로 EASY / MEDIUM / HARD 중 하나)
- content: 질문 내용
- intent: 출제 의도 (한 문장)
- keywords: 답변에 필수로 들어가야되는 핵심 키워드 리스트 (2~4개)
"""

    try:
        # OpenAI Structured Output 호출
        # response_format에 Pydantic 모델을 지정해 정형화된 응답 보장
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {
                    "role": "system",
                    "content": "당신은 CS 기술면접 전문가입니다. 반드시 JSON 형식으로만 응답하세요.",
                },
                {
                    "role": "user",
                    "content": prompt
                },
            ],
            response_format=QuestionGenerateResponseDTO,
        )

        result = completion.choices[0].message.parsed

        # Structured Output 파싱 실패 시 None 반환 방어
        if result is None:
            logger.error(f"OpenAI Structured Output 파싱 실패: {completion.choices[0].message}")
            raise HTTPException(
                status_code=502,
                detail="질문 생성 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
            )

        # LLM 응답 검증: 요청한 질문 수와 실제 반환된 질문 수 일치 여부 확인
        if len(result.questions) != request.questionCount:
            raise HTTPException(
                status_code=502,
                detail=f"LLM이 요청한 질문 수와 다른 수의 질문을 반환했습니다. "
                       f"(요청: {request.questionCount}, 반환: {len(result.questions)})"
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        # 네트워크/인증/rate-limit 등 OpenAI 호출 에러 처리 (내부 에러 로깅)
        logger.exception(f"OpenAI API 호출 실패: {str(e)}")
        raise HTTPException(
            status_code=502,
            detail="질문 생성 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
        )
