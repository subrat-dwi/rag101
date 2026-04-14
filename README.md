# RAG Learning Project (Personal Reference)

This is my personal Retrieval-Augmented Generation (RAG) playground.

Primary goal: load a local PDF into Qdrant, retrieve relevant chunks for a query, and generate answers with Groq (`llama-3.1-8b-instant`) through a FastAPI service and RQ background jobs.

## What This Project Does

- Indexes a PDF from `data_files/` into a Qdrant collection named `rag-learning`.
- Uses `all-MiniLM-L6-v2` embeddings (Hugging Face) for both indexing and retrieval.
- Exposes a FastAPI server with:
  - `POST /chat` to enqueue a query.
  - `GET /result` to fetch async job output.
- Uses RQ + Redis-compatible backend (Valkey container on `6379`) for async processing.

## Current Architecture

- Vector DB: Qdrant (`http://localhost:6333`)
- Queue backend: Valkey/Redis protocol (`localhost:6379`)
- API: FastAPI served by Uvicorn (`0.0.0.0:8000`)
- Worker: RQ worker consuming queued chat jobs
- LLM provider: Groq
- Document source: one PDF file in `data_files/`

High-level flow:

1. `index.py` loads and chunks the PDF.
2. Chunks are embedded and written to Qdrant collection `rag-learning`.
3. API receives query at `POST /chat` and enqueues job.
4. RQ worker calls `generate_response()`.
5. Retrieval pulls top-k similar chunks from Qdrant.
6. Groq generates final answer from retrieved context.
7. Client polls `GET /result?job_id=...`.

## Project Structure

- `index.py`: PDF loading, chunking, embedding, and indexing into Qdrant.
- `retrieve.py`: retrieval + prompt construction + Groq completion.
- `server.py`: FastAPI routes (`/`, `/chat`, `/result`).
- `main.py`: app entrypoint (`uvicorn.run`).
- `client/rq_client.py`: RQ queue initialization.
- `queues/worker.py`: job function wrapper (`process_query`).
- `docker-compose.yml`: Qdrant + Valkey containers.
- `data_files/`: source documents for indexing.

## Prerequisites

- Python 3.10+ (3.11 recommended)
- Docker + Docker Compose
- Internet access for:
  - Hugging Face embedding model download (first run)
  - Groq API calls

## Environment Setup

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create `.env` in project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Notes:

- `.env` is ignored by git (good).
- If `GROQ_API_KEY` is missing, generation calls fail when the worker executes `retrieve.py`.

## Start Services

Start Qdrant and Valkey:

```bash
docker compose up -d
```

Check health quickly:

```bash
docker ps
curl http://localhost:6333
```

Expected:

- Qdrant listening on `6333`
- Valkey listening on `6379`

## Index Documents (One-time or After Document Changes)

Run indexer:

```bash
python index.py
```

What it does:

- Loads `data_files/The_Courage_to_be_Disliked_How_to_Change_Your_Life_and_Achieve_Real.pdf`
- Splits into chunks (`chunk_size=1000`, `chunk_overlap=200`)
- Writes embeddings to collection `rag-learning`

When to rerun:

- PDF content changed
- Collection wiped/reset
- Chunking or embedding settings changed

## Run API + Worker

Terminal 1 (API):

```bash
python main.py
```

Terminal 2 (RQ worker):

```bash
rq worker --with-scheduler
```

Worker can also be run without scheduler for this app:

```bash
rq worker
```

## API Usage

### 1) Health check

```bash
curl http://localhost:8000/
```

### 2) Submit chat query

```bash
curl -X POST "http://localhost:8000/chat?query=What%20is%20the%20core%20message%20of%20the%20book%3F"
```

Response shape:

```json
{
  "status": "Query has been received and is being processed",
  "job-id": "<rq_job_id>"
}
```

### 3) Poll job result

```bash
curl "http://localhost:8000/result?job_id=<rq_job_id>"
```

Possible responses:

- `Job is still processing`
- `Job completed` + answer text
- `Job failed`
- `Job not found`

## Internal Defaults (Important)

- Qdrant URL: `http://localhost:6333`
- Qdrant collection: `rag-learning`
- Embedding model: `all-MiniLM-L6-v2`
- Groq model: `llama-3.1-8b-instant`
- Retrieval top-k: `5`

## Quick Restart Checklist

1. Activate venv.
2. `docker compose up -d`
3. `python index.py` (if needed)
4. Start API: `python main.py`
5. Start worker: `rq worker --with-scheduler`
6. Call `/chat`, then poll `/result`

## Troubleshooting

### API starts but `/chat` never completes

- Worker is not running.
- Fix: start `rq worker --with-scheduler` in a separate terminal.

### `Job failed`

Common causes:

- `GROQ_API_KEY` missing or invalid.
- Qdrant unavailable on `6333`.
- Collection `rag-learning` missing (indexing never run).

Check:

```bash
curl http://localhost:6333
```

Then rerun:

```bash
python index.py
```

### Slow first query

Expected on first run because embedding model may download and cache.

### Empty/weak answers

Possible reasons:

- Chunking config not ideal for the document.
- Query too broad.
- Retrieval top-k too low.

Try:

- Increasing `top_k` in `retrieve.py`
- Adjusting chunk size/overlap in `index.py`

## Personal Notes for Future Me

- This is a single-developer reference project, not a packaged product.
- Keep infra simple: Qdrant + Valkey via Docker is enough.
- If changing collection name, update both `index.py` and `retrieve.py`.
- If changing embedding model, re-index everything.
- If the PDF filename changes, update path in `index.py`.

## Known Gaps / Future Improvements

- Add request/response schemas with Pydantic models.
- Add proper logging and structured error handling.
- Add endpoint to list/query job status in a cleaner format.
- Add configurable settings via env vars (host, ports, models, top-k, collection).
- Add tests for indexing and retrieval flow.
- Add multi-document ingestion pipeline.

## Handy Commands

Bring containers down:

```bash
docker compose down
```

View worker logs (if started in shell, use that terminal output).

Rebuild index after collection reset:

```bash
python index.py
```

Run server with uvicorn directly (alternative):

```bash
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

## Reference: Main Runtime Components

- `index()` in `index.py`: ingestion + indexing.
- `retrieve()` in `retrieve.py`: vector similarity search.
- `generate_response()` in `retrieve.py`: retrieval + Groq answer generation.
- `chat()` in `server.py`: enqueue async job.
- `get_result()` in `server.py`: poll async status/result.
