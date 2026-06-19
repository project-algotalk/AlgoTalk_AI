# STT 품질 검증 임계값
MAX_SILENCE_RATIO = 70.0
MIN_ASR_CONFIDENCE = 0.3
MAX_NO_SPEECH_PROB = 0.3


def should_fail_stt_quality(
    answer_text: str,
    silence_ratio: float,
    asr_confidence: float,
    avg_no_speech_prob: float,
) -> bool:
    """
    Whisper 결과가 실제 답변으로 사용하기 어려운지 판단한다.

    no_speech_prob는 짧은 발화/녹음 환경에서 실제 답변이 있어도 높게 나올 수 있으므로,
    텍스트가 있고 ASR 신뢰도가 양호한 경우에는 단독 실패 조건으로 사용하지 않는다.
    """
    has_answer_text = bool(answer_text and answer_text.strip())

    if not has_answer_text:
        return True

    poor_silence = silence_ratio > MAX_SILENCE_RATIO
    poor_confidence = asr_confidence < MIN_ASR_CONFIDENCE
    poor_no_speech = avg_no_speech_prob > MAX_NO_SPEECH_PROB

    # 실제 답변 텍스트가 추출된 경우에는 하나의 보조 지표만 나쁘다고 버리지 않고,
    # 두 개 이상의 지표가 함께 나쁠 때만 품질 실패로 처리합니다.
    return sum([poor_silence, poor_confidence, poor_no_speech]) >= 2
