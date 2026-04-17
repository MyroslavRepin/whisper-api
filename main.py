import base64
import os
import shutil

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.background import BackgroundTasks
from uuid import uuid4
from whisper import load_model
from typing import Dict
import resend
from dotenv import load_dotenv
load_dotenv()
app = FastAPI()
model = load_model("base")
resend.api_key = os.environ["RESEND_API_KEY"]
jobs = {}

def transcribe_audio(file_path, job_id):
    transcription = model.transcribe(file_path)
    jobs[job_id]["result"] = transcription
    jobs[job_id]["status"] = "completed"
    transaction_text = transcription["text"]
    send_mail(transaction_text)
    return transcription["text"]

def send_mail(transcription_text: str) -> Dict:
    params: resend.Emails.SendParams = {
        "from": "Acme <whisper-api@myroslavrepin.com>",
        "to": ["myroslavrepin@gmail.com"],
        "subject": "Transcription finished",
        "attachments": [
            {
                "filename": "transcript.txt",
                "content": base64.b64encode(transcription_text.encode("utf-8")).decode("utf-8"),
            }
        ],
        "text": "Transcription in an attachment"
    }
    try:
        email: resend.Emails.SendResponse = resend.Emails.send(params)
    except Exception as e:
        raise e
    return email

@app.post("/transcribe")
def transcribe(file: UploadFile, background_tasks: BackgroundTasks):
    job_id = str(uuid4())
    jobs[job_id] = {"status": "processing", "result": None}

    file_path = f"records/saved_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    background_tasks.add_task(transcribe_audio, file_path, job_id)
    return {"job_id": job_id, "filename": file.filename}

@app.get("/status/{job_id}")
def status(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job