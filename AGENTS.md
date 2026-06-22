# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## Project Overview

This is a FastAPI-based audio transcription service using OpenAI Whisper. It accepts audio file uploads, transcribes them asynchronously, and delivers results via email with S3 storage capabilities.

## Architecture

The project is split into backend (Python/FastAPI) and frontend (Vue.js):

### Backend Structure
- `main.py` - FastAPI application entry point (currently has test S3 code commented out)
- `backend/api/transcribe.py` - API router with transcription endpoint
- `backend/services/transcribe.py` - Core transcription logic using Whisper model
- `backend/services/email.py` - Email delivery via Resend API
- `backend/services/s3.py` - S3 file upload functionality (boto3)
- `backend/config.py` - Pydantic settings configuration with S3 client factory
- `backend/redis.py` - Redis integration (currently empty/stub)

### Key Data Flow
1. Audio file uploaded via `/transcribe` endpoint (API router in `backend/api/transcribe.py:16`)
2. File saved locally to `records/saved_{filename}`
3. Background task triggered to transcribe audio (`backend/services/transcribe.py:7`)
4. Whisper model processes audio and extracts text
5. Transcription sent via email as attachment using Resend API (`backend/services/email.py:5`)

### Configuration
All settings loaded from `.env` file via `backend/config.py`:
- `resend_api_key` - API key for email service
- `whisper_model` - Whisper model size (default: "tiny")
- `s3_username`, `s3_password`, `s3_bucket`, `s3_endpoint` - S3 credentials

Email hardcoded to send from `whisper-api@myroslavrepin.com` to `myroslavrepin@gmail.com`.

## Development Commands

### Backend
```bash
# Install dependencies (using uv)
uv sync

# Run development server
uv run uvicorn main:app --reload

# Note: main.py currently has the FastAPI app commented out and contains test S3 upload code
```

### Frontend
```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Important Notes

- **Whisper Model**: Loaded once at module import in `backend/services/transcribe.py:5`. Changing model requires service restart.
- **Background Tasks**: Transcription runs asynchronously via FastAPI BackgroundTasks to avoid blocking API response.
- **File Storage**: Audio files saved to local `records/` directory. S3 upload function exists but isn't integrated into transcription flow.
- **API Router Issue**: `backend/api/transcribe.py` has duplicate `@app.post("/")` decorators (lines 10 and 15) - second one will override first.
- **Main Entry Point**: The FastAPI app initialization in `main.py` is commented out. Uncomment to enable the API.
