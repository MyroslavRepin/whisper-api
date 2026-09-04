import os

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

    # Sync on purpose: BackgroundTasks awaits coroutines on the event loop,
    # so an async version blocks the whole server for the entire transcription.
    # A sync function is run in Starlette's threadpool instead.
    def process_audio_file(self, file_key: str, to_email: str):
        """Orchestrate complete workflow: download → transcribe → email → cleanup"""
        file_path = os.path.join(settings.tmp_file_location, file_key)
        out_path = None

        try:
            file_path = str(
                self.storage_service.download_file(
                    bucket_name=settings.s3_bucket,
                    file_key=file_key,
                    download_path=file_path,
                )
            )
            out_path = self.transcription_service.transcribe_audio(file_path)

            with open(out_path, encoding="utf-8") as f:
                transcription_text = f.read().strip()

            # Resend rejects an empty text body, so silence needs its own message.
            self.email_service.send_email(
                to=to_email,
                subject="Transcription completed!",
                text=transcription_text or "No speech detected in this audio.",
            )

            logger.info(f"Transcription completed and email sent to {to_email}")
            return {"status": "success"}
        except Exception as exc:
            # Nothing upstream can catch this: the request already returned.
            # Log it and tell the user instead of failing silently.
            logger.opt(exception=exc).error(f"Workflow failed for {file_key}")
            self._notify_failure(to_email)
            return {"status": "failed", "error": str(exc)}
        finally:
            self._cleanup(file_path, out_path)

    def _notify_failure(self, to_email: str) -> None:
        try:
            self.email_service.send_email(
                to=to_email,
                subject="Transcription failed",
                text=(
                    "Your audio could not be transcribed. "
                    "Please try uploading it again."
                ),
            )
        except Exception as exc:
            logger.opt(exception=exc).error(
                f"Could not send failure notice to {to_email}"
            )

    def _cleanup(self, *paths: str | None) -> None:
        for path in paths:
            if not path:
                continue
            try:
                os.remove(path)
            except FileNotFoundError:
                pass
            except OSError as exc:
                logger.warning(f"Could not remove {path}: {exc}")
