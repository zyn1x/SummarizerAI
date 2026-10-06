# SummarizerAI 🧠⚡
> **Local-First AI Content Intelligence Platform for Multi-Modal Sources with Verifiable Citations and Grounded RAG.**

Built with **React + Vite + Tailwind CSS** on the frontend and **Python + FastAPI + PostgreSQL (pgvector ready) / SQLite** on the backend.

---

## 🌟 Key Features

1. **Universal Multi-Source Ingestion**:
   - 📄 **PDF Documents**: PyMuPDF (`pymupdf` / `fitz`) with automatic page tracking and section header detection.
   - 📝 **TXT / Markdown**: Multi-encoding detection and heading-aware structural extraction.
   - 🌐 **Websites & Articles**: Trafilatura clean content extraction with BeautifulSoup fallback and section preservation.
   - 🎥 **YouTube Videos**: `yt-dlp` subtitle extraction with exact second-accurate timestamps (`MM:SS` / `HH:MM:SS`) mapped to video chunks.
   - 🔬 **Research Papers**: ArXiv API metadata extraction, automated PDF retrieval, and scientific section parsing (Abstract, Methods, Results, Discussion).

2. **Security & Data Protection**:
   - 🛡️ **SSRF Protection**: IP resolution checks against private ranges (RFC 1918, link-local, loopback, cloud metadata endpoints).
   - 🔒 **File Validation**: Filename sanitization, extension whitelisting, and configurable file size limits.
   - 🧹 **Automatic Cleanup**: Temporary files and scratch downloads are safely deleted after ingestion.

3. **Provider-Agnostic LLM Architecture**:
   - ⚡ **Google Gemini as Default Cloud Engine**: Powered by Google's official `google-genai` SDK v2 with `gemini-3.8-flash` for high-speed generation and `gemini-embedding-2` for 3072-dimensional embeddings / RAG.
   - 🦙 **Ollama as Optional Local Runner**: Seamless local inference (`llama3.2`, `mistral`, `qwen2.5`, etc.) with zero mandatory requirement during standard development.
   - 🛡️ **Offline Intelligent Fallback**: Built-in TF-IDF vector embeddings and extractive synthesis that ensures 100% functionality out-of-the-box even without an API key or under rate limits.
   - ☁️ **Cloud LLM Readiness**: Modular architecture with **zero API keys exposed to the frontend**.

4. **Hierarchical Document Analysis**:
   - Map-Reduce pipeline for long documents: batches chunks into section syntheses before generating cohesive executive or detailed deliverables.

5. **Deterministic Backend-Controlled Citations**:
   - Zero hallucination of page numbers, timestamps, or section headings. The backend matches claims strictly to verified source chunks (`[p. 2]`, `[03:45]`, `[Introduction]`).
   - Clickable citation chips in the UI automatically highlight the corresponding chunk in the Source Inspector.

6. **Interactive Post-Ingestion Workspace**:
   - **Summary**: Choose between Executive, Detailed, or Bulleted formats.
   - **Key Points**: Core arguments, quantitative findings, and strategic takeaways.
   - **Actionable Insights with 6 Target Goals**:
     - 🎓 *Study for an Exam*: High-yield definitions, key formulas, flashcard concepts & sample exam questions.
     - 🧠 *Understand the Topic*: ELI5 mental models, analogies, and first-principles breakdown.
     - 🛠️ *Implement the Method*: Engineering steps, algorithm pseudocode, edge cases & test protocols.
     - 🚀 *Apply to a Project*: Architectural integration blueprint, performance budgets & risk matrices.
     - 🧭 *Find Research Gaps*: Critical review of unstated assumptions, methodology limits & novel hypotheses.
     - 📊 *Prepare a Presentation*: 5-slide deck outline, slide titles, bullet points, speaker notes & audience Q&A.
   - **Ask Questions (Document Q&A / Grounded RAG)**:
     - Vector similarity search over chunks.
     - Evidence grounding badge with explicit guardrails when the source does not contain enough information.

7. **Persistence & Performance**:
   - PostgreSQL schema with pgvector-ready embeddings.
   - Built-in SQLite (`aiosqlite`) fallback for instant zero-configuration local execution.
   - Analysis caching: Ingested documents and analyses are persisted and reused instantly without redundant LLM calls.

---

## 🛠️ Technology Stack

| Layer | Technologies & Libraries |
| :--- | :--- |
| **Backend Framework** | **Python 3.11+**, **FastAPI**, **Uvicorn**, **Pydantic v2**, **pydantic-settings** |
| **LLM & Embeddings** | **Google GenAI SDK (`google-genai` v2)**, **Gemini 3.8 Flash**, **Gemini Embedding 2**, **Ollama API Client** (Optional Local Provider) |
| **Vector Search / RAG** | **NumPy**, **Scikit-learn** (Cosine similarity, Top-$k$ ranker), **PGVector** (PostgreSQL) |
| **Document Ingestion** | **PyMuPDF (`fitz`)**, **Trafilatura**, **BeautifulSoup4**, **`yt-dlp`**, **ArXiv API Client**, **HTTPX** |
| **Database & ORM** | **SQLAlchemy 2.0 (AsyncIO)**, **aiosqlite** (SQLite dev), **asyncpg** (PostgreSQL prod) |
| **Frontend UI** | **React 19**, **TypeScript**, **Vite**, **Tailwind CSS**, **Lucide React**, **react-markdown**, **remark-gfm** |
| **DevOps & Testing** | **Docker**, **Docker Compose**, **Pytest**, **pytest-asyncio** |

---

## 🏛️ System Architecture

```
SummarizerAI
├── frontend/                   # React 19 + TypeScript + Vite + Tailwind CSS UI
│   ├── src/
│   │   ├── components/         # Modular React components
│   │   │   ├── Navbar.tsx
│   │   │   ├── UploadSection.tsx
│   │   │   ├── ProcessingProgress.tsx
│   │   │   ├── ActionSelector.tsx
│   │   │   ├── ResultsView.tsx
│   │   │   ├── SourcePreview.tsx
│   │   │   ├── QAChat.tsx
│   │   │   ├── DocumentLibrary.tsx
│   │   │   └── Footer.tsx
│   │   ├── api.ts              # Strongly-typed API client
│   │   ├── App.tsx             # Workspace state machine
│   │   └── index.css           # Glassmorphic Tailwind theme
├── src/summarizerai/           # Python + FastAPI Backend
│   ├── api/                    # REST API endpoints & routers
│   ├── ingestion/              # PDF, TXT, Web, YouTube & ArXiv extractors
│   ├── processing/             # Normalization & Canonical Document model
│   ├── chunking/               # Structure-aware chunking preserving metadata
│   ├── llm/                    # Provider abstraction (Gemini, Ollama, Fallback)
│   ├── actions/                # Summaries, Key Points, Actionable Insights, Citations
│   ├── services/               # RAG vector retrieval & Document caching service
│   ├── models/                 # SQLAlchemy async models
│   ├── schemas/                # Pydantic v2 schemas
│   ├── database/               # Async engine (PostgreSQL / SQLite)
│   └── main.py                 # FastAPI application entrypoint
├── tests/                      # Automated unit and integration test suite
├── requirements.txt            # Python production dependencies with pinned bounds
├── pyproject.toml              # Build system configuration
├── docker-compose.yml          # Postgres + pgvector, Redis, and Backend
├── Dockerfile                  # Multi-stage production container build
└── .env.example                # Documented configuration variables
```

---

## 🚀 Quick Start (Local Setup)

### 1. Prerequisites
- **Python >= 3.11** (Python 3.12 or 3.13 recommended)
- **Node.js >= 18** & npm
- [Ollama](https://ollama.com/) *(Optional, only needed if you want local offline LLMs)*

### 2. Backend Setup
```bash
# Clone the repository
git clone https://github.com/zyn1x/SummarizerAI.git
cd SummarizerAI

# Create and activate a Python virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install backend dependencies via requirements.txt
pip install -r requirements.txt

# Or if you use uv:
uv pip install -r requirements.txt

# Copy environment variables
cp .env.example .env

# Start the FastAPI backend server
python -m uvicorn summarizerai.main:app --host 127.0.0.1 --port 8000 --reload
```
API Documentation will be live at: `http://127.0.0.1:8000/api/docs`

### 3. Frontend Setup
```bash
# In a new terminal window:
cd frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## ⚙️ LLM Provider Configuration

SummarizerAI defaults to **Google Gemini** for instant, high-performance cloud inference with zero local GPU hardware requirements.

### 1. Google Gemini Setup (Default & Recommended)
1. Generate a free API key at [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Configure your `.env` file:
   ```bash
   LLM_PROVIDER=gemini
   GEMINI_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL=gemini-3.8-flash
   GEMINI_EMBEDDING_MODEL=gemini-embedding-2
   ```

### 2. Ollama Local LLM Setup (Optional)
To run completely offline with local open-weights models:
```bash
# 1. Set LLM_PROVIDER=ollama in your .env
# 2. Start Ollama and pull your models
ollama serve
ollama pull llama3.2
ollama pull nomic-embed-text
```

*Note: If neither Gemini nor Ollama is configured or reachable, SummarizerAI automatically and gracefully activates its built-in local offline engine so you can explore and use the application immediately.*

---

## 🐳 Docker Deployment

To launch the full production stack with PostgreSQL, pgvector, and Redis:
```bash
docker compose up --build -d
```
Services exposed:
- **Backend API**: `http://localhost:8000`
- **Postgres with pgvector**: `localhost:5432`
- **Redis**: `localhost:6379`

---

## 🧪 Running Tests

The test suite validates chunking, metadata preservation, SSRF protection, sanitization, and the end-to-end API pipeline:
```bash
pytest -v tests/
```

---

## 🔒 Security Best Practices Implemented

- **SSRF Protection**: Resolves domain names to IP addresses and rejects `127.0.0.0/8`, `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `169.254.0.0/16`, and loopback addresses.
- **Input Sanitization**: Whitelists extensions (`.pdf`, `.txt`, `.md`), enforces file size boundaries, and sanitizes filenames to prevent directory traversal.
- **Backend-Enforced Citations**: Prevents hallucinated page numbers or timestamps by deterministically binding citations to ingested chunk coordinates.

---

## 📄 License
MIT License.

---

### Built by Dikshant Sharma
