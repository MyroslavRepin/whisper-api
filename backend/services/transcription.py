from faster_whisper import WhisperModel
from loguru import logger


class TranscriptionService:
    def __init__(
        self,
        model: WhisperModel,
    ):
        self.model: WhisperModel = model

    def transcribe_audio(self, file_path):
        logger.debug(f"Transcribing audio file: {file_path}")
        segments, info = self.model.transcribe(file_path)
        logger.debug(f"Transcription info: detected_language={info.language}, duration={info.duration}s")
        transcription_text = " ".join([segment.text for segment in segments])
        logger.debug(f"Transcription complete: {len(transcription_text)} chars")
        return transcription_text
