from fastapi import APIRouter
from fastapi import UploadFile
from fastapi.background import BackgroundTasks
import shutil

from backend.services.transcribe import transcribe_audio

app = APIRouter()

@app.post("/")
def root():
    return {
        "status": "ok",
    }
@app.post("/")
def transcribe(file: UploadFile, background_tasks: BackgroundTasks):

    file_path = f"records/saved_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    background_tasks.add_task(transcribe_audio, file_path)
    return {"filename": file.filename}
