# Whisper API

Audio transcription service using OpenAI Whisper with asynchronous job processing, object storage, and email delivery.

## Architecture

### Backend
- **FastAPI** - REST API server
- **PostgreSQL** - Job tracking and persistence
- **MinIO** - Object storage for audio files
- **ARQ** - Asynchronous task queue for transcription jobs
- **Whisper** - OpenAI's speech-to-text model (local inference)
- **Mailgun** - Email delivery for transcription results

### Frontend
- **Vue.js** - User interface for file upload and job submission

## MVP Flow

1. **Vue form** - User enters email + selects audio file → clicks upload
2. **Vue** does `POST /jobs/init` → FastAPI creates job in PostgreSQL (status: `pending`), generates presigned PUT URL from MinIO, returns `{job_id, upload_url}`
3. **Vue** uploads file directly to MinIO via `upload_url` (PUT request)
4. **Vue** does `POST /jobs/{job_id}/confirm` → FastAPI enqueues job to ARQ
5. **ARQ worker** picks up job → downloads file from MinIO → runs Whisper locally → updates status in PostgreSQL
6. **Post-transcription** → Mailgun sends transcription text to email → deletes file from MinIO → status: `done`

## Project Structure

```
whisper-api/
├── backend/
│   ├── api/
│   │   └── transcribe.py      # API routes
│   ├── services/
│   │   ├── transcribe.py      # Whisper transcription logic
│   │   ├── email.py           # Email delivery
│   │   └── s3.py              # MinIO/S3 integration
│   ├── config.py              # Configuration management
│   └── redis.py               # Redis client (for ARQ)
├── frontend/
│   └── (Vue.js application)
├── main.py                    # FastAPI application entry point
└── pyproject.toml             # Python dependencies (uv)
```

## Development

### Backend Setup

```bash
# Install dependencies
uv sync

# Run development server
uv run uvicorn main:app --reload
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

## Configuration

Create a `.env` file in the project root:

```env
# Email
RESEND_API_KEY=your_resend_key
# (Migrating to Mailgun)

# Whisper
WHISPER_MODEL=tiny

# MinIO/S3
S3_USERNAME=your_username
S3_PASSWORD=your_password
S3_BUCKET=your_bucket
S3_ENDPOINT=your_endpoint_url

# PostgreSQL
DATABASE_URL=postgresql://user:pass@localhost/whisper_api

# Redis (for ARQ)
REDIS_URL=redis://localhost:6379
```

## API Endpoints

### Current (Legacy)
- `POST /transcribe` - Direct upload and transcribe (synchronous)

### MVP (In Development)
- `POST /jobs/init` - Initialize job, get presigned upload URL
- `POST /jobs/{job_id}/confirm` - Confirm upload and start transcription
- `GET /jobs/{job_id}` - Get job status (planned)

## Roadmap

See [ROADMAP.md](ROADMAP.md) for detailed development plans and feature backlog.

## License

[Add license information]
