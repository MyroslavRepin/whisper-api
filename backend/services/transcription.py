import os
import subprocess
import tempfile
import time
from math import ceil
from pathlib import Path

from faster_whisper import WhisperModel
from loguru import logger

from backend.core.config import settings
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
            out_path = file_path + ".txt"
            duration = self.get_duration(file_path)
            chunk_seconds = max(1, settings.transcription_chunk_seconds)
            chunk_count = max(1, ceil(duration / chunk_seconds))

            with tempfile.TemporaryDirectory(
                prefix="whisper_chunks_", dir=settings.tmp_file_location
            ) as chunk_dir:
                char_count = self._transcribe_chunks(
                    file_path=file_path,
                    out_path=out_path,
                    duration=duration,
                    chunk_seconds=chunk_seconds,
                    chunk_dir=Path(chunk_dir),
                    chunk_count=chunk_count,
                )

            elapsed = time.perf_counter() - start
            logger.debug(
                f"Transcription complete for {file_path} in {elapsed:.2f} seconds, "
                f"{char_count} characters transcribed across {chunk_count} chunks"
            )
            return out_path
        except Exception as e:
            logger.error(f"Transcription failed for {file_path}: {e}")
            raise

    def _transcribe_chunks(
        self,
        file_path: str,
        out_path: str,
        duration: float,
        chunk_seconds: int,
        chunk_dir: Path,
        chunk_count: int,
    ) -> int:
        char_count = 0
        with open(out_path, "w", encoding="utf-8") as out_file:
            for index in range(chunk_count):
                start_seconds = index * chunk_seconds
                remaining_seconds = duration - start_seconds
                current_chunk_seconds = min(chunk_seconds, remaining_seconds)
                chunk_path = chunk_dir / f"chunk_{index:04d}.wav"

                logger.debug(
                    f"Preparing chunk {index + 1}/{chunk_count}: "
                    f"start={start_seconds:.2f}s duration={current_chunk_seconds:.2f}s"
                )
                self._extract_chunk(
                    source_path=file_path,
                    chunk_path=chunk_path,
                    start_seconds=start_seconds,
                    duration_seconds=current_chunk_seconds,
                )

                segments, _ = self.model.transcribe(str(chunk_path))
                chunk_text_parts = [segment.text.strip() for segment in segments]
                chunk_text = " ".join(part for part in chunk_text_parts if part)

                if chunk_text:
                    if char_count:
                        out_file.write("\n\n")
                    out_file.write(chunk_text)
                    char_count += len(chunk_text)

                chunk_path.unlink(missing_ok=True)

        return char_count

    def _extract_chunk(
        self,
        source_path: str,
        chunk_path: Path,
        start_seconds: int,
        duration_seconds: float,
    ) -> None:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-v",
                "error",
                "-ss",
                str(start_seconds),
                "-t",
                str(duration_seconds),
                "-i",
                source_path,
                "-ac",
                "1",
                "-ar",
                "16000",
                str(chunk_path),
            ],
            check=True,
        )

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
