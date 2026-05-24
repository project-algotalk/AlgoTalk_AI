from pydantic import BaseModel
# STT 분석 응답 DTO
class SttResponseDTO(BaseModel):
    answerText: str          # STT 변환 텍스트
    answerDuration: int      # 발화 시간 (초)
    wpm: int                 # 말하기 속도 (Words Per Minute)
    silenceRatio: float      # 무음 비율 (0.0 ~ 100.0)
    asrConfidence: float     # ASR 신뢰도 (0.0 ~ 1.0)
    fillerCount: int         # 추임새 횟수
    fillerRatio: float       # 추임새 비율 (0.0 ~ 100.0)