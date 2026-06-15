import logging
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
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

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


# Remove default loguru handler and add custom one
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG",
    enqueue=True,  # Thread-safe logging for background tasks
)

# Intercept uvicorn and FastAPI logging
logging.getLogger("uvicorn").handlers = [InterceptHandler()]
logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]
logging.getLogger("uvicorn.error").handlers = [InterceptHandler()]
logging.getLogger("fastapi").handlers = [InterceptHandler()]

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def load_model():
    logger.info(f"Loading Whisper model: {settings.whisper_model}")
    app.state.whisper_model = WhisperModel(
        settings.whisper_model,
        device="cpu",
        compute_type="int8",
    )
    logger.info("Whisper model loaded successfully")


# Include API v1 routes FIRST (before static files)
app.include_router(transcription_api, prefix="/api/v1")

# Serve static frontend files
frontend_dist = Path(__file__).parent / "frontend" / "dist"
if frontend_dist.exists():
    # Mount static assets (js, css, etc) at /assets
    assets_dir = frontend_dist / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    # Catch-all: serve SPA files with proper fallback
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        requested = frontend_dist / full_path
        if requested.is_file():
            return FileResponse(requested)
        return FileResponse(frontend_dist / "index.html")
else:
    logger.warning(f"Frontend dist not found at {frontend_dist}")

    @app.get("/")
    async def root():
        return {"message": "Hello, World!"}
