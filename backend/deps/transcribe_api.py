from fastapi import HTTPException, Request
from pydantic import BaseModel, EmailStr

from backend.services.transcription import TranscriptionService


def get_transcription_service(request: Request) -> TranscriptionService:
    model = getattr(request.app.state, "whisper_model", None)
    if model is None:
        raise HTTPException(503, "Transcription model is still loading. Try again.")
    return TranscriptionService(model)


class TranscriptionEmailSchema(BaseModel):
    email: EmailStr
