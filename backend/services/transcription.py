import os
import subprocess
import time

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
            start = time.perf_counter()
            segments, info = self.model.transcribe(file_path)

            out_path = file_path + ".txt"
            char_count = 0
            with open(out_path, "w", encoding="utf-8") as f:
                for segment in segments:
                    f.write(segment.text + " ")
                    char_count += len(segment.text)

            elapsed = time.perf_counter() - start
            logger.debug(
                f"Transcription complete for {file_path} in {elapsed:.2f} seconds, {char_count} characters transcribed"
            )
            return out_path
        except Exception as e:
            logger.error(f"Transcription failed for {file_path}: {e}")
            raise

    def get_duration(self, path: str) -> float:
        out = subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "csv=p=0",
                path,
            ],
            text=True,
        )
        return float(out)


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
