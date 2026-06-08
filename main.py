import logging
import sys

from fastapi import FastAPI
from faster_whisper import WhisperModel
from loguru import logger

from backend.api.v1.transcription import app as transcription_api
from backend.core.config import settings


# Configure loguru
class InterceptHandler(logging.Handler):
    """Intercept standard logging and redirect to loguru"""

    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


# Remove default loguru handler and add custom one
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
)

# Intercept uvicorn and FastAPI logging
logging.getLogger("uvicorn").handlers = [InterceptHandler()]
logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]
logging.getLogger("uvicorn.error").handlers = [InterceptHandler()]
logging.getLogger("fastapi").handlers = [InterceptHandler()]

app = FastAPI()


@app.on_event("startup")
async def load_model():
    logger.info(f"Loading Whisper model: {settings.whisper_model}")
    app.state.whisper_model = WhisperModel(
        settings.whisper_model,
        device="cpu",
        compute_type="int8",
    )
    logger.info("Whisper model loaded successfully")


@app.get("/")
async def root():
    return {"message": "Hello, World!"}


# Include API v1 routes
app.include_router(transcription_api, prefix="/v1")
