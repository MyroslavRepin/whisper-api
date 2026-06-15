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
        try:
            logger.debug(f"Transcribing: {file_path}")
            segments, info = self.model.transcribe(file_path)

            out_path = file_path + ".txt"
            char_count = 0
            with open(out_path, "w", encoding="utf-8") as f:
                for segment in segments:
                    f.write(segment.text + " ")
                    char_count += len(segment.text)

            logger.debug(
                f"Transcription complete ({char_count} chars, language: {info.language})"
            )
            return out_path
        except Exception as e:
            logger.error(f"Transcription failed for {file_path}: {e}")
            raise


def transcribe_workflow(
    transcription_service: TranscriptionService,
    file_path: str,
    email_service: EmailService,
):
    logger.info(f"Starting transcription workflow for {file_path}")
    try:
        transcription_text = transcription_service.transcribe_audio(file_path)
        logger.debug("Text transcription complete")
        os.remove(file_path)
        # Todo: I might need delete file from S3

        try:
            logger.debug("Sending email with transcription")
            email_service.send_mail(transcription_text)
            logger.debug("Email sent successfully")
        except Exception as e:
            logger.error(f"Failed to send email: {e}")

        logger.info(f"Workflow completed for {file_path}")
    except Exception as e:
        logger.error(f"Workflow failed for {file_path}: {e}")
        if os.path.exists(file_path):
            os.remove(file_path)
