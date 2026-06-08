from pydantic import BaseModel
from enum import Enum

# STT 답변 여부
class AnswerStatus(str, Enum):
    ANSWERED = "ANSWERED"  # 답변 있음
    SKIPPED = "SKIPPED"    # 답변 없음 (사용자가 발화하지 않음 / FE에서 처리)
    QUALITY_FAIL = "QUALITY_FAIL"  # STT 품질 기준 미달 (Whisper 환각 가능성 높음)

# STT 분석 응답 DTO
class SttResponseDTO(BaseModel):
    answerStatus: AnswerStatus  # 답변 상태(ANSWERED, QUALITY_FAIL)
    answerText: str          # STT 변환 텍스트
    answerDuration: int      # 발화 시간 (초)
    wpm: int                 # 말하기 속도 (Words Per Minute)
    silenceRatio: float      # 무음 비율 (0.0 ~ 100.0)
    asrConfidence: float     # ASR 신뢰도 (0.0 ~ 1.0)
    fillerCount: int         # 추임새 횟수
    fillerRatio: float       # 추임새 비율 (0.0 ~ 100.0)