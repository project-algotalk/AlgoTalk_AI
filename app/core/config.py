from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
# .env 파일 절대경로 설정
try:
    BASE_DIR = Path(__file__).resolve().parents[2]
except NameError:
    BASE_DIR = Path.cwd().parents[1]
_ENV_FILE = BASE_DIR / ".env"
# 애플리케이션 설정 클래스
# pydantic_settings를 사용해 .env 파일의 환경변수를 타입 안전하게 관리
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ENV_FILE,
        env_file_encoding="utf-8"
    )

    OPENAI_API_KEY: str
# 모듈 레벨 인스턴스 생성 (다른 모듈에서 import해서 사용)
settings = Settings()
