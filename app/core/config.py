from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# 애플리케이션 설정 클래스
# pydantic_settings를 사용해 .env 파일의 환경변수를 타입 안전하게 관리
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # OpenAI API 키 (.env의 OPEN_API_KEY 값과 매핑)
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")

# 모듈 레벨 인스턴스 생성 (다른 모듈에서 import해서 사용)
settings = Settings()