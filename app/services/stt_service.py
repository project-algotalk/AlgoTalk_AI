from fastapi import HTTPException, UploadFile
import logging
import tempfile
import os
import math
import re
from openai import OpenAI
from app.schemas.stt import SttResponseDTO
# 설정 모듈에서 환경변수 로드
from app.core.config import settings
logger = logging.getLogger(__name__)
# OpenAI 클라이언트 초기화
client = OpenAI(api_key=settings.OPENAI_API_KEY)
# 추임새 목록
FILLER_WORDS = {"음", "어", "네", "그", "저", "뭐", "아", "음~", "어~", "그~", "저~"}
def count_fillers(text: str) -> tuple[int, float]:
    """
    STT 변환 텍스트에서 추임새 횟수와 비율 계산
    """
    # 문장부호 제거 후 단어 분리
    cleaned = re.sub(r'[^\w\s]', '', text)
    words = cleaned.split()
    total_words = len(words)

    if total_words == 0:
        return 0, 0.0

    filler_count = sum(1 for w in words if w in FILLER_WORDS)
    filler_ratio = round((filler_count / total_words) * 100, 2)

    return filler_count, filler_ratio
def transcribe_audio(file: UploadFile) -> SttResponseDTO:
    """
    음성 파일을 텍스트로 변환하고 STT 분석 지표를 반환
    Whisper API 호출 → 텍스트 변환 + ASR confidence + 무음 비율 + WPM + 추임새 계산
    """
    tmp_path: str | None = None
    try:
        # 1. 임시 파일로 저장
        suffix = os.path.splitext(file.filename)[-1] or ".webm"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(file.file.read())
            tmp_path = tmp.name

        # 2. Whisper API 호출 (추임새 포함 유도 + verbose_json으로 segment 정보 포함)
        with open(tmp_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="ko",
                response_format="verbose_json",
                prompt="음, 어, 네, 그, 저, 뭐, 아"  # 추임새 포함 유도
            )

        # 3. 텍스트 추출
        answer_text = response.text.strip()

        # 4. 발화 시간 계산
        answer_duration = int(response.duration) if response.duration else 0

        # 5. WPM 계산 (단어 수 / 발화 시간(초) × 60)
        word_count = len(answer_text.split())
        wpm = int((word_count / answer_duration) * 60) if answer_duration > 0 else 0

        # 6. ASR confidence 평균 계산
        segments = response.segments or []
        if segments:
            confidences = [math.exp(seg.avg_logprob) for seg in segments]
            asr_confidence = round(sum(confidences) / len(confidences), 4)
        else:
            asr_confidence = 0.0

        # 7. 무음 비율 계산
        silence_duration = 0.0
        if segments and answer_duration > 0:
            silence_duration += segments[0].start
            for i in range(1, len(segments)):
                gap = segments[i].start - segments[i - 1].end
                if gap > 0:
                    silence_duration += gap
            last_end = segments[-1].end
            silence_duration += max(0, answer_duration - last_end)

        silence_ratio = round((silence_duration / answer_duration) * 100, 2) if answer_duration > 0 else 0.0

        # 8. 추임새 횟수 및 비율 계산
        filler_count, filler_ratio = count_fillers(answer_text)

        return SttResponseDTO(
            answerText=answer_text,
            answerDuration=answer_duration,
            wpm=wpm,
            silenceRatio=silence_ratio,
            asrConfidence=asr_confidence,
            fillerCount=filler_count,
            fillerRatio=filler_ratio,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"STT 변환 실패: {str(e)}")
        raise HTTPException(
            status_code=502,
            detail="음성 변환 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
        )
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)