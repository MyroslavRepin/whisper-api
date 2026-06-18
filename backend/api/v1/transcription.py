import os
import subprocess
import tempfile
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, Form, UploadFile
from fastapi.exceptions import HTTPException
from loguru import logger
from pydantic.networks import EmailStr

from backend.core.config import settings
from backend.deps.transcribe_api import (
    TranscriptionEmailSchema,
    get_transcription_service,
)
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
    email: EmailStr = Form(...),
    transcription_service: TranscriptionService = Depends(get_transcription_service),
):
    logger.info(f"Received transcription request")
    logger.info(f"Audio file: {audio_file.filename}, content_type: {audio_file.content_type}")
    logger.info(f"Email: {email}")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".audio") as tmp:
        tmp_path = tmp.name
        while chunk := await audio_file.read(1024 * 1024):
            tmp.write(chunk)

    try:
        try:
            duration = transcription_service.get_duration(tmp_path)
        except (subprocess.CalledProcessError, ValueError):
            raise HTTPException(400, "Unable to recognize audio")

        if duration > settings.max_file_duration:
            raise HTTPException(
                400, detail=f"Audio {duration / 60:.0f} min — limit 55 min"
            )

        to_email = email
        file_key = f"temp_{uuid.uuid4()}_{audio_file.filename}"
        logger.info("Uploading file to S3")
        with open(tmp_path, "rb") as f:
            storage_service.upload_file(f, settings.s3_bucket, file_key)
        logger.info("Uploading file to S3 finished")

        audio_workflow = AudioTranscriptionWorkflow(
            transcription_service=transcription_service,
            email_service=EmailService(settings.resend_api_key),
            storage_service=storage_service,
        )
        logger.info("Transcription workflow started in background")
        background_tasks.add_task(
            audio_workflow.process_audio_file, file_key=file_key, to_email=to_email
        )

    finally:
        os.unlink(tmp_path)

    return {"status": "processing"}
