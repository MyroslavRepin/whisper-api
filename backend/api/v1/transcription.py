import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, UploadFile
from loguru import logger

from backend.core.config import settings
from backend.deps.transcribe_api import get_transcription_service
from backend.services.email import EmailService
from backend.services.storage import StorageService
from backend.services.transcription import TranscriptionService, transcribe_workflow
from backend.services.workflow import AudioTranscriptionWorkflow

app = APIRouter()

storage_service = StorageService()


@app.post("/transcribe", response_model=None)
async def transcribe_audio_api(
    audio_file: UploadFile,
    background_tasks: BackgroundTasks,
    transcription_service: TranscriptionService = Depends(get_transcription_service),
):
    file_key = f"temp_{uuid.uuid4()}_{audio_file.filename}"
    logger.info("Uploading file to S3")
    storage_service.upload_file(audio_file.file, settings.s3_bucket, file_key)
    logger.info("Uploading file to S3 finished")
    audio_workflow = AudioTranscriptionWorkflow(
        transcription_service=transcription_service,
        email_service=EmailService(settings.resend_api_key),
        storage_service=storage_service,
    )
    logger.info("Transcription workflow started in background")
    background_tasks.add_task(audio_workflow.process_audio_file, file_key=file_key)
    return {"status", "processing"}
