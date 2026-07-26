# CodeSense AI

Paste a GitHub repo, get an AI-generated architecture overview, code analysis,
a chat interface grounded in the actual code, generated docs, and generated
unit tests.

## Architecture

- **Backend**: FastAPI + a LangGraph pipeline (`ingest → embed → architecture → code_analysis`)
- **Vector store**: Chroma (cosine similarity)
- **LLM**: Google Gemini (`google-genai` SDK)
- **Chunking**: tree-sitter, supports Python, JavaScript, TypeScript, Java, Go, C, C++, Ruby, Rust, PHP, and C#
- **Persistence**: SQLite (analyzed repos + chat history survive a restart)
- **Frontend**: React + Vite

## Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend/.env`:

```
GEMINI_API_KEY=your_real_gemini_api_key
# Optional - only needed as a fallback for private repos. You can also
# supply a token per-request in the UI instead.
GITHUB_TOKEN=
CHROMA_PERSIST_DIR=./chroma_db
SQLITE_DB_PATH=./data/codesense.db
```

Run it:

```bash
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Docker

```bash
docker compose up --build
```

## Features

- **Grounded chat**: retrieval results are filtered by similarity before ever
  reaching the LLM. If nothing relevant is found, you get an honest
  "I don't have enough context to answer that" instead of a guess.
- **Live analysis progress**: the frontend streams progress via
  Server-Sent Events as each pipeline stage completes, instead of a single
  blocking spinner.
- **Export**: download a Markdown report bundling the architecture overview,
  code analysis, and evaluation metrics for a repo.
- **Repo history**: previously analyzed repos are cached and can be reopened
  instantly without re-running analysis.
- **Private repos**: optionally supply a GitHub personal access token
  (per-request, never persisted) to clone private repos.
- **Multi-language support**: chunking works across 10 languages, not just
  Python/JS/TS.
- **Evaluation metrics**: the export includes a metrics section - chunk/
  language coverage, static analysis issue counts, and how often chat
  answers were actually grounded vs. falling back.

## Security note

`.env` is gitignored. Never commit real API keys or personal access tokens.
If a key has ever been shared or committed by mistake, rotate it immediately.
