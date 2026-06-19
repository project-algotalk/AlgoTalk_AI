import logging
import os
from logging.handlers import TimedRotatingFileHandler

ENV = os.getenv("APP_ENV", "local")
LOG_DIR = os.getenv("LOG_DIR", "/data/log/algotalk/ai-service" if ENV == "prod" else "./logs")
LOG_FILE_NAME = os.getenv("LOG_FILE_NAME", "applog.log")
LOG_FORMAT = "%(asctime)s [%(levelname)-5s] %(name)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging() -> None:
    formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT)
    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    # 콘솔 핸들러 (모든 환경 공통)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # 파일 핸들러 (local, prod 공통으로 켜되 경로만 다름)
    os.makedirs(LOG_DIR, exist_ok=True)
    file_handler = TimedRotatingFileHandler(
        filename=os.path.join(LOG_DIR, LOG_FILE_NAME),
        when="midnight", # 자정마다
        interval=1,
        backupCount=30, # 30일치 보관
        encoding="utf-8",
    )
    file_handler.suffix = "%Y-%m-%d"
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    root_logger.setLevel(logging.INFO if ENV == "prod" else logging.DEBUG)

    for uvicorn_logger_name in ("uvicorn", "uvicorn.access", "uvicorn.error"):
        uvicorn_logger = logging.getLogger(uvicorn_logger_name)
        uvicorn_logger.handlers = root_logger.handlers
        uvicorn_logger.propagate = False