from fastapi import HTTPException
from openai import OpenAI
import logging
from app.schemas.interview import (
    QuestionGenerateRequestDTO,   # 질문 생성 요청 DTO
    QuestionGenerateResponseDTO,  # 질문 생성 응답 DTO
    CsValidationRequestDTO,      # CS 질문 검증 요청 DTO
    CsValidationResponseDTO,     # CS 질문 검증 응답 DTO
)
# 설정 모듈에서 환경변수 로드
from app.core.config import settings
logger = logging.getLogger(__name__)
# OpenAI 클라이언트 초기화
client = OpenAI(api_key=settings.OPENAI_API_KEY)
def generate_questions(request: QuestionGenerateRequestDTO) -> QuestionGenerateResponseDTO:

    categories_str = ", ".join(request.categories)

    # 히스토리 블록 생성
    if request.previousQuestions:
        history_block = "\n".join([f"- {q}" for q in request.previousQuestions[:30]])
    else:
        history_block = "- (없음)"

    prompt = f"""
당신은 CS 기술면접 전문가입니다.
아래 조건을 모두 만족하는 질문을 생성하세요.

[입력]
- 카테고리: {categories_str}
- 질문 수: {request.questionCount}개
- 모든 출력은 한국어

[출제 원칙]
1) 주제 다양성
- 카테고리 내 다양한 세부 주제를 골고루 출제하세요.
- 특정 주제에 편중되지 않도록 하세요.
- 한 세션 내에서 동일한 세부 주제는 최대 1회만 허용합니다.

2) 관점 다양화
- 아래 관점을 골고루 섞어서 출제:
  - 개념 정의형
  - 비교/트레이드오프형
  - 설계/아키텍처형
  - 장애/트러블슈팅형
  - 성능 최적화형
  - 실무 의사결정/사례형
- 동일 관점의 질문이 2개를 초과해 연속되지 않게 할 것

3) 중복 방지
- 동일 세션 내 동일한 세부 주제의 완전 중복 금지
- "~이란 무엇인가요?" 패턴 반복 최소화
- intent가 서로 겹치지 않게 작성

4) 난이도 분포
- EASY / MEDIUM / HARD를 균형 배치 (MEDIUM 중심)

[재출제 방지 히스토리]
- 아래는 같은 사용자가 최근에 이미 받은 질문 목록입니다.
- 의미적으로 유사한 질문도 재출제하지 마세요.
- 단, 같은 주제 자체를 금지하는 것은 아닙니다.
- 같은 주제를 사용한다면 질문의 관점, 상황, 요구하는 답변 방향을 반드시 다르게 만드세요.
{history_block}

[출력 형식]
각 질문은 반드시 다음 필드만 포함:
- order: 질문 순서 (1부터 시작)
- category: 해당 카테고리명
- difficulty: 난이도 (EASY / MEDIUM / HARD 중 하나)
- content: 질문 내용
- intent: 출제 의도 (한 문장)
- keywords: 핵심 키워드 리스트 (2~4개)

중요:
- Structured Output(JSON 스키마)에 정확히 맞춰서만 출력
- 스키마 외 필드 추가 금지
"""

    try:
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
            message = completion.choices[0].message
            raw_content = getattr(message, "content", None)
            logger.error(
                "OpenAI Structured Output 파싱 실패. message=%s raw_content=%s",
                message, raw_content
            )
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
        # 네트워크/인증/rate-limit 등 OpenAI 호출 에러 처리
        logger.exception(f"OpenAI API 호출 실패: {str(e)}")
        raise HTTPException(
            status_code=502,
            detail="질문 생성 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
        )


def validate_cs_questions(request: CsValidationRequestDTO) -> CsValidationResponseDTO:
    """
    CS 관련 질문 여부 검증 함수
    사용자가 직접 입력한 질문들이 CS 관련 질문인지 LLM 기반으로 판단
    """

    # 질문 목록을 번호 붙인 문자열로 변환 (프롬프트 삽입용)
    questions_str = "\n".join([f"{i+1}. {q}" for i, q in enumerate(request.questions)])

    # CS 질문 검증 프롬프트 구성
    prompt = f"""
    아래 질문들이 IT/기술 직무 면접에서 출제될 수 있는 질문인지 판단해주세요.

    [isValid=true 조건] - 아래 중 하나 이상에 해당해야 합니다:
    - CS 기술 지식: 자료구조, 알고리즘, 운영체제, 네트워크, 데이터베이스, 프로그래밍 언어, 시스템 설계 등
    - IT 직무 전문성: 서비스 기획/PM/PO 역량, 개발 방법론, 소프트웨어 아키텍처, UX/UI, 데이터 분석 등
    - 반드시 문장 형태의 질문이어야 합니다 (단어 하나, 짧은 구문은 질문이 아님)
    - 면접 답변이 가능한 구체적인 질문이어야 합니다

    [isValid=false 조건] - 아래 중 하나라도 해당하면 false:
    - 단어 하나 또는 의미 없는 짧은 구문 (예: "기획", "네트워크", "OS")
    - IT/기술과 무관한 일반 상식, 취미, 개인 생활 관련
    - 질문 형태가 아닌 것 (문장이 완성되지 않은 것)
    - 면접 질문으로 볼 수 없는 내용

    질문 목록:
    {questions_str}

    각 질문에 대해 반드시 다음 형식으로 판단하세요:
    - questionText: 질문 내용 (원문 그대로)
    - isValid: true / false
    - reason: 판단 이유 (한 문장, 한국어로)
    """

    try:
        # OpenAI Structured Output 호출
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {
                    "role": "system",
                    "content": "당신은 CS 기술면접 전문가입니다. 질문이 CS 관련인지 판단해주세요. 반드시 JSON 형식으로만 응답하세요.",
                },
                {
                    "role": "user",
                    "content": prompt
                },
            ],
            response_format=CsValidationResponseDTO,
        )

        result = completion.choices[0].message.parsed

        # Structured Output 파싱 실패 시 None 반환 방어
        if result is None:
            message = completion.choices[0].message
            raw_content = getattr(message, "content", None)
            logger.error(
                "CS 질문 검증 Structured Output 파싱 실패. message=%s raw_content=%s",
                message, raw_content
            )
            raise HTTPException(
                status_code=502,
                detail="질문 검증 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
            )

        # LLM 응답 검증: 입력 질문 수와 결과 수 일치 여부 확인
        if len(result.results) != len(request.questions):
            logger.error(
                "CS 검증 결과 수 불일치. 요청: %d, 반환: %d",
                len(request.questions), len(result.results)
            )
            raise HTTPException(
                status_code=502,
                detail="질문 검증 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        # 네트워크/인증/rate-limit 등 OpenAI 호출 에러 처리
        logger.exception(f"CS 질문 검증 실패: {str(e)}")
        raise HTTPException(
            status_code=502,
            detail="질문 검증 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
        )