# Whisper API

Audio transcription service hosted on Raspberry Pi using OpenAI's Whisper model.

## Tech Stack

- **FastAPI** - Python web framework
- **Vue.js + Vite** - Frontend UI
- **faster-whisper** - Local Whisper inference (optimized)
- **S3-compatible storage** - Audio file storage (MinIO or similar)
- **Resend** - Email delivery
- **Docker Compose** - Single-container production deployment
- **uv** - Python package manager

## Project Structure

```
whisper-api/
├── backend/
│   ├── api/
│   │   └── v1/
│   │       └── transcription.py   # API endpoints
│   ├── core/
│   │   ├── config.py              # Settings (Pydantic)
│   │   └── redis.py               # Redis stub (unused)
│   ├── deps/
│   │   └── transcribe_api.py      # FastAPI dependencies
│   └── services/
│       ├── email.py               # Resend email service
│       ├── storage.py             # S3 upload/download
│       ├── transcription.py       # Whisper model inference
│       └── workflow.py            # Orchestration logic
├── frontend/
│   ├── src/
│   │   ├── App.vue                # Main upload UI
│   │   ├── components/            # Vue components
│   │   └── main.js
│   ├── .env.development           # Dev API URL
│   ├── .env.production            # Prod API URL (relative path)
│   └── vite.config.js
├── main.py                        # FastAPI app + static file serving
├── Dockerfile                     # Backend dev Dockerfile
├── Dockerfile.production          # Multi-stage production build
├── docker-compose.yml             # Production deployment
└── pyproject.toml                 # Python dependencies (uv)
```

## How It Works

1. User uploads audio file via Vue frontend
2. Backend receives file at `POST /api/v1/transcribe`
3. File uploaded to S3-compatible storage
4. Background task triggered:
   - Downloads file from S3
   - Transcribes using faster-whisper
   - Sends transcript via Resend email
   - Cleans up temporary file
5. User receives email with transcription text

## Prerequisites

- **Docker + Docker Compose** (production)
- **Node.js 20+** (development frontend)
- **Python 3.14+** (development backend)
- **uv** (install: `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- **S3-compatible storage** (MinIO, AWS S3, etc.)
- **Resend API key** (email delivery)

## Development

Run backend and frontend separately with hot-reload:

### Backend

```bash
# Install dependencies
uv sync

# Run dev server (port 8080)
uv run uvicorn main:app --reload
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run dev server (port 5173)
npm run dev
```

Frontend dev mode hits `http://localhost:8080/api/v1` (configured in `frontend/.env.development`).

## Production

Single container serves built frontend + API on port 8080:

```bash
# Build and run
docker compose up --build

# Access at http://localhost:8080
```

Production build:
1. Vite builds frontend to static files
2. Static files copied into backend image
3. FastAPI serves:
   - API routes at `/api/v1/*`
   - Static assets at `/assets/*`
   - SPA fallback to `index.html` for client-side routing

## Environment Variables

### Backend (.env in project root)

```env
# Email delivery
RESEND_API_KEY=re_xxxxx

# Whisper model size (tiny, base, small, medium, large)
WHISPER_MODEL=tiny
MAX_FILE_DURATION=10800
TRANSCRIPTION_CHUNK_SECONDS=600

# S3-compatible storage
S3_USERNAME=admin
S3_PASSWORD=your_password
S3_BUCKET=whisper-audio
S3_ENDPOINT=https://s3.example.com

# Temp file location
TMP_FILE_LOCATION=/tmp/
```

### Frontend (Vite build-time variables)

**`frontend/.env.development`** (local dev):
```env
VITE_API_URL=http://localhost:8080/api/v1
```

**`frontend/.env.production`** (Docker build):
```env
VITE_API_URL=/api/v1
```

Production uses relative path since frontend and API served from same origin.

## API Endpoints

### POST /api/v1/transcribe

Upload audio file for transcription.

**Request:**
- `audio_file` (multipart/form-data) - Audio file
- `email` (multipart/form-data) - Recipient email address

**Response:**
```json
{"status": "processing"}
```

Transcription runs asynchronously. Audio files up to 3 hours are accepted by default.
Long files are split into 10-minute chunks on disk, transcribed sequentially, and joined
into one email response to keep Raspberry Pi memory usage bounded.

## Notes

- Hardcoded recipient: `myroslavrepin@gmail.com` (see `backend/services/workflow.py:36`)
- No job status tracking (fire-and-forget)
- No authentication/rate limiting
- Whisper model loaded once at startup (change requires restart)
- See `ROADMAP.md` for planned features (PostgreSQL, ARQ worker, presigned URLs)
