from fastapi import HTTPException
from openai import OpenAI
import logging
from app.schemas.evaluation import (
    AnswerEvaluationRequestDTO,
    AnswerEvaluationResponseDTO,
)
from app.core.config import settings

logger = logging.getLogger(__name__)
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def evaluate_answer(request: AnswerEvaluationRequestDTO) -> AnswerEvaluationResponseDTO:
    """
    LLM 기반 면접 답변 내용 평가 함수
    - answerTest가 있는 경우: 전체 평가(점수, 피드백, 모범 답변, 학습 팁, 꼬리 질문)
    - answerText가 비어있거나 질문과 무관한 내용인 경우: 모범 답변, 학습 팁, 꼬리 질문은 그대로 반환하되 contentScore=0, feedback=null로 평가
    """

    keywords_str = ", ".join(request.keywords) if request.keywords else "없음"
    has_answer = bool(request.answerText and request.answerText.strip())

    if has_answer:
        # 답변이 있는 경우: 전체 평가
        prompt = f"""
당신은 CS 기술면접 전문 평가자입니다.
아래 면접 질문과 사용자의 답변을 평가해주세요.

[면접 질문]
{request.questionText}

[핵심 키워드]
{keywords_str}

[사용자 답변]
{request.answerText}

[평가 기준]
1. 핵심 키워드 포함 여부: 답변에 핵심 키워드가 포함되어 있는가
2. 개념 정확성: 기술적 내용이 정확한가
3. 답변 완성도: 질문에 충분히 답변했는가

[출력 형식]
- contentScore: 0~25점 사이의 정수
  - 23~25: 핵심 키워드 모두 포함, 개념 정확, 완성도 높음
  - 18~22: 대부분의 키워드 포함, 개념 대체로 정확
  - 13~17: 일부 키워드 포함, 개념 부분적으로 정확
  - 8~12: 키워드 부족, 개념 설명 미흡
  - 0~7: 핵심 내용 누락, 개념 오류 있음
- feedback: 답변에 대한 구체적인 피드백 (한국어)
  - 잘한 점: 답변에서 좋았던 부분
  - 부족한 점: 아쉬웠던 부분과 개선 방향
  - 추가하면 좋을 내용: 답변에 포함되면 더 좋을 내용
- modelAnswer: 모범 답변 (핵심 키워드를 포함한 이상적인 답변, 한국어)
- studyTip: 이 질문과 관련하여 더 공부하면 좋을 내용 (2~3문장, 한국어)
- followUpQuestions: 면접관이 이어서 물어볼 수 있는 꼬리 질문 2~3개 (한국어 리스트)

중요:
- 답변이 비어있거나 질문과 무관한 내용이면 contentScore는 0점
- 모든 출력은 반드시 한국어로 작성
    """
    else:
        # 답변이 없는 경우: 모범 답변, 학습 팁, 꼬리 질문만 생성
        prompt = f"""
당신은 CS 기술면접 전문 평가자입니다.
아래 면접 질문과 사용자의 답변을 평가해주세요.

[면접 질문]
{request.questionText}

[핵심 키워드]
{keywords_str}

[출력 형식]
- contentScore: 반드시 0 (답변 없음)
- feedback: 반드시 None (답변 없음. 피드백 불필요)
- modelAnswer: 모범 답변 (핵심 키워드를 포함한 이상적인 답변, 한국어)
- studyTip: 이 질문과 관련하여 더 공부하면 좋을 내용 (2~3문장, 한국어)
- followUpQuestions: 면접관이 이어서 물어볼 수 있는 꼬리 질문 2~3개 (한국어 리스트)

중요:
- 답변이 비어있거나 질문과 무관한 내용이면 contentScore는 0점
- feedback: 반드시 None
- 모든 출력은 반드시 한국어로 작성
    """

    try:
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {
                    "role": "system",
                    "content": "당신은 CS 기술면접 전문 평가자입니다. 반드시 JSON 형식으로만 응답하세요.",
                },
                {
                    "role": "user",
                    "content": prompt
                },
            ],
            response_format=AnswerEvaluationResponseDTO,
        )

        result = completion.choices[0].message.parsed

        # Structured Output 파싱 실패 시 방어
        if result is None:
            message = completion.choices[0].message
            raw_content = getattr(message, "content", None)
            logger.error(
                "OpenAI Structured Output 파싱 실패. message=%s raw_content=%s",
                message, raw_content
            )
            raise HTTPException(
                status_code=502,
                detail="답변 평가 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"답변 평가 실패: {str(e)}")
        raise HTTPException(
            status_code=502,
            detail="답변 평가 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
        )