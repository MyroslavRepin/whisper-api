# Whisper API - Project Roadmap

## Project Vision

Audio transcription service using OpenAI Whisper with asynchronous job processing, object storage, and email delivery.

## Current Status

Migrating from simple synchronous upload + transcribe flow to production-ready MVP architecture with:
- PostgreSQL job tracking
- MinIO object storage with presigned URLs
- ARQ async task queue
- Mailgun email delivery


## MVP Flow

1. **Vue form** - User enters email + selects audio file → clicks upload
2. **Vue** does `POST /jobs/init` → FastAPI creates job in PostgreSQL (status: `pending`), generates presigned PUT URL from MinIO, returns `{job_id, upload_url}`
3. **Vue** uploads file directly to MinIO via `upload_url` (PUT request)
4. **Vue** does `POST /jobs/{job_id}/confirm` → FastAPI enqueues job to ARQ
5. **ARQ worker** picks up job → downloads file from MinIO → runs Whisper locally → updates status in PostgreSQL
6. **Post-transcription** → Mailgun sends transcription text to email → deletes file from MinIO → status: `done`

## Goals

### Short-term Goals (Next 1-2 weeks)
- [ ] Set up PostgreSQL schema for job tracking
- [ ] Implement MinIO presigned URL generation
- [ ] Create `/jobs/init` and `/jobs/{job_id}/confirm` endpoints
- [ ] Set up ARQ worker for async transcription
- [ ] Integrate Mailgun for email delivery
- [ ] Update Vue frontend for new multi-step flow

### Medium-term Goals (Next 1-2 months)
- [ ] Add job status polling/webhook for frontend
- [ ] Implement retry logic for failed jobs
- [ ] Add support for multiple Whisper model sizes
- [ ] Create admin dashboard for job monitoring
- [ ] Add rate limiting and authentication

### Long-term Goals (Future)
- [ ] Multi-language transcription support
- [ ] Real-time transcription streaming
- [ ] Speaker diarization
- [ ] Custom vocabulary/domain models
- [ ] Enterprise SSO integration

## Technical Improvements Needed

- [ ] Replace hardcoded email addresses with job-specific recipients
- [ ] Add proper logging and monitoring
- [ ] Set up health checks for ARQ workers
- [ ] Implement database migrations (Alembic)
- [ ] Add environment-specific configs (dev/staging/prod)
- [ ] Containerize application (Docker/Docker Compose)

## Features to Build

- [ ] Job status API endpoint (`GET /jobs/{job_id}`)
- [ ] File format validation (audio types only)
- [ ] File size limits and error handling
- [ ] Transcription result storage in database
- [ ] Download transcription as TXT/SRT/VTT
- [ ] Batch transcription support

## Known Issues

- [ ] `main.py` has FastAPI app commented out with test S3 code
- [ ] `backend/api/transcribe.py` has duplicate `@app.post("/")` decorators
- [ ] Current implementation uses local file storage instead of S3/MinIO
- [ ] No job status tracking or persistence
- [ ] Resend API used instead of planned Mailgun

## Ideas & Backlog
<!-- Nice-to-have features or ideas to explore later -->
-
-

## Notes
<!-- Any additional thoughts, decisions, or context -->
