import os

from faster_whisper import WhisperModel
from loguru import logger

from backend.services.email import EmailService


class TranscriptionService:
    def __init__(
        self,
        model: WhisperModel,
    ):
        self.model: WhisperModel = model

    def transcribe_audio(self, file_path):
        logger.debug(f"Transcribing audio file: {file_path}")
        segments, info = self.model.transcribe(file_path)
        logger.debug(
            f"Transcription info: detected_language={info.language}, duration={info.duration}s"
        )
        transcription_text = " ".join([segment.text for segment in segments])
        logger.debug(f"Transcription complete: {len(transcription_text)} chars")
        return transcription_text


def transcribe_workflow(
    transcription_service: TranscriptionService,
    file_path: str,
    email_service: EmailService,
):
    logger.info(f"Starting transcription workflow for {file_path}")
    transcription_text = transcription_service.transcribe_audio(file_path)
    os.remove(file_path)
    try:
        email_service.send_mail(transcription_text)
        logger.debug(f"Email sent successfully for {file_path}")
    except Exception as e:
        logger.error(f"Error sending email for {file_path}: {e}")

    logger.info(f"Transcription workflow completed for {file_path}")
