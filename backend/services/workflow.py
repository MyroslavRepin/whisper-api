import os

from fastapi import BackgroundTasks, UploadFile
from loguru import logger

from backend.core.config import settings
from backend.services.email import EmailService
from backend.services.storage import StorageService
from backend.services.transcription import TranscriptionService


class AudioTranscriptionWorkflow:
    def __init__(
        self,
        transcription_service: TranscriptionService,
        email_service: EmailService,
        storage_service: StorageService,
    ):
        self.transcription_service = transcription_service
        self.email_service = email_service
        self.storage_service = storage_service

    async def process_audio_file(self, file_key: str, to_email: str):
        """Orchestrate complete workflow: upload → transcribe → email → cleanup"""
        file_path = os.path.join(settings.tmp_file_location, file_key)

        file_path = self.storage_service.download_file(
            bucket_name=settings.s3_bucket,
            file_key=file_key,
            download_path=file_path,
        )
        file_path = str(file_path)
        transcript_text = self.transcription_service.transcribe_audio(file_path)

        self.email_service.send_email(
            to=to_email,
            subject="Transcription completed!",
            text=transcript_text,
        )

        os.remove(file_path)

        logger.info(f"Transcription completed and email sent to {to_email}")
        return {"status": "success"}
