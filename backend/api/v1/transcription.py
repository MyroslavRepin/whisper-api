import os
import subprocess
import tempfile
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, Form, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from loguru import logger
from pydantic.networks import EmailStr

from backend.core.config import settings
from backend.deps.transcribe_api import get_transcription_service
from backend.services.email import EmailService
from backend.services.storage import StorageService
from backend.services.transcription import TranscriptionService
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
    logger.info(
        f"Transcription request: file={audio_file.filename}, "
        f"content_type={audio_file.content_type}, email={email}"
    )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".audio") as tmp:
        tmp_path = tmp.name
        while chunk := await audio_file.read(1024 * 1024):
            tmp.write(chunk)

    try:
        size = os.path.getsize(tmp_path)
        logger.debug(f"Temp file written: {tmp_path} ({size} bytes)")
        if size == 0:
            raise HTTPException(400, "Audio file is empty")

        try:
            duration = await run_in_threadpool(
                transcription_service.get_duration, tmp_path
            )
        except (subprocess.CalledProcessError, ValueError, OSError) as exc:
            logger.warning(f"Could not read duration of {audio_file.filename}: {exc}")
            raise HTTPException(400, "Unable to recognize audio")

        if duration > settings.max_file_duration:
            raise HTTPException(
                400,
                detail=(
                    f"Audio {duration / 60:.0f} min - "
                    f"limit {settings.max_file_duration / 60:.0f} min"
                ),
            )

        file_key = f"temp_{uuid.uuid4()}_{audio_file.filename}"
        logger.info("Uploading file to S3")
        try:
            with open(tmp_path, "rb") as f:
                await run_in_threadpool(
                    storage_service.upload_file, f, settings.s3_bucket, file_key
                )
        except Exception as exc:
            logger.opt(exception=exc).error(f"S3 upload failed for {file_key}")
            raise HTTPException(502, "Storage is unavailable. Try again later.")
        logger.info("Uploading file to S3 finished")

        audio_workflow = AudioTranscriptionWorkflow(
            transcription_service=transcription_service,
            email_service=EmailService(settings.resend_api_key),
            storage_service=storage_service,
        )
        logger.info("Transcription workflow started in background")
        background_tasks.add_task(
            audio_workflow.process_audio_file, file_key=file_key, to_email=email
        )

    finally:
        try:
            os.unlink(tmp_path)
        except OSError as exc:
            logger.warning(f"Could not remove temp file {tmp_path}: {exc}")

    return {"status": "processing"}
