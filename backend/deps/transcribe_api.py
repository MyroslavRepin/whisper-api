from fastapi import Request

from backend.services.transcription import TranscriptionService


def get_transcription_service(request: Request):
    model = request.app.state.whisper_model
    return TranscriptionService(model)
