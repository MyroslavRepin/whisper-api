from fastapi import Request
from pydantic import BaseModel, EmailStr

from backend.services.transcription import TranscriptionService


def get_transcription_service(request: Request):
    model = request.app.state.whisper_model
    return TranscriptionService(model)


class TranscriptionEmailSchema(BaseModel):
    email: EmailStr
