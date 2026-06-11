import email
import os
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, UploadFile
from loguru import logger

from backend.core.config import settings
from backend.deps.transcribe_api import get_transcription_service
from backend.services.email import EmailService
from backend.services.storage import StorageService
from backend.services.transcription import TranscriptionService, transcribe_workflow

app = APIRouter()

storage_service = StorageService()


@app.post("/transcribe", response_model=None)
async def transcribe_audio_api(
    audio_file: UploadFile,
    background_tasks: BackgroundTasks,
    transcription_service: TranscriptionService = Depends(get_transcription_service),
):
    # Upload the audio file to S3
    try:
        file_name = f"temp_{uuid.uuid4()}_{audio_file.filename}"
        logger.info(f"Uploading file to S3: {file_name}")
        storage_service.upload_file(audio_file.file, settings.s3_bucket, file_name)
        logger.info(f"Upload to S3 successful: {file_name}")

        try:
            file_path = f"/tmp/{file_name}"
            storage_service.download_file(settings.s3_bucket, file_name, file_path)
            email_service = EmailService(settings.resend_api_key)

            background_tasks.add_task(
                email_service.send_email,
                to="myroslavrepin@gmail.com",
                subject="test email",
                text="This is a test email",
            )

            os.remove(file_path)

            logger.info(f"Transcription completed for {file_name}")
            return {"status": "success"}
        except Exception as e:
            logger.error(f"Transcription error for {file_name}: {e}")
            return {"status": "error", "error": str(e)}
        return {"status": "success", "message": "Audio file uploaded to S3"}
    except Exception as e:
        logger.error(f"S3 upload error for {audio_file.filename}: {e}")
        return {"status": "error", "error": str(e)}
