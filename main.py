from fastapi import FastAPI

# from backend.api import transcribe
# from backend.services.s3 import upload_file_to_s3

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello, World!"}


# upload_file_to_s3(" main.py", "whisper-audio", "main.py")
