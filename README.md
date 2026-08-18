# InsightAI — Prompt-Based Reporting System

> A full-stack AI-powered analytics platform that transforms raw CSV/Excel datasets into rich, interactive visual dashboards and natural-language-grounded reports — all running 100% locally on your machine.

---

## ✨ Key Features

| Feature | Description |
| :--- | :--- |
| 📊 **Visual Dashboard** | Instantly generates 8–15 Plotly charts (bar, line, pie, scatter, histogram, heatmap, box) without any LLM calls |
| 🤖 **AI Report Generation** | Uses RAG (ChromaDB + sentence-transformers) + Google Gemini to generate grounded, context-rich analytical reports |
| 🗂️ **Dataset History** | Previously uploaded datasets are stored in MySQL and can be reused without re-uploading |
| 📑 **Report History** | All generated AI reports are saved and accessible from the History page |
| 🔐 **JWT Authentication** | Secure registration/login flow with protected routes across all services |
| 🖥️ **Dedicated Dashboard Tab** | Visual dashboards open in a new browser tab (`/dashboard/view/:fileId`) with a responsive 2-column grid layout |
| 🔒 **Privacy First** | All data processing is local; only metadata snippets reach the Google Gemini API |
| 📥 **Report Download** | Generated reports can be downloaded as self-contained interactive HTML files |

---

## 🏗️ System Architecture

The project is structured into three decoupled, independently running services:

```
                  ┌──────────────────────────────────────────┐
                  │            React Frontend                │
                  │   Vite · React 19 · Tailwind v4 · Plotly │
                  │          http://localhost:5173           │
                  └──────────────────┬───────────────────────┘
                                     │
                            REST API + JWT Auth
                                     │
                                     ▼
                  ┌──────────────────────────────────────────┐
                  │           FastAPI Backend                │
                  │      SQLAlchemy · PyMySQL · JWT          │
                  │          http://localhost:8000           │
                  └────────┬─────────────────┬───────────────┘
                           │                 │
              File Forward │                 │ Read / Write
                (multipart)│                 │ Blobs & Metadata
                           │                 ▼
                           │    ┌─────────────────────────┐
                           │    │       MySQL Database    │
                           │    │  users · files · reports│
                           │    └─────────────────────────┘
                           ▼
                  ┌──────────────────────────────────────────┐
                  │          FastAPI AI Microservice         │
                  │ Pandas · ChromaDB · Sentence-Transformers│
                  │          http://localhost:8001           │
                  └──────────────────┬───────────────────────┘
                                     │
                         Google Gemini API (Phase 2 only)
                                     │
                                     ▼
                           Google Generative AI
```

---

## 📁 Project Structure

```
InsightAI - Prompt Based Reporting System/
│
├── README.md                        ← This file (project root)
│
├── backend/                         ← FastAPI REST API Service (port 8000)
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py              ← Register, Login, Me, Logout
│   │   │   ├── upload.py            ← Upload dataset + GET upload history
│   │   │   ├── report.py            ← AI report generation & retrieval
│   │   │   ├── dashboard.py         ← Dashboard stats + visual chart generation
│   │   │   └── history.py           ← User report history
│   │   ├── models/                  ← SQLAlchemy ORM models
│   │   ├── schemas/                 ← Pydantic request/response schemas
│   │   ├── core/                    ← JWT config, DB config, security helpers
│   │   └── main.py                  ← FastAPI app entry point
│   ├── requirements.txt
│   └── README.md                    ← Backend API endpoint reference
│
├── ai-service/                      ← FastAPI AI Microservice (port 8001)
│   ├── app/
│   │   ├── api/
│   │   │   ├── dashboard.py         ← POST /api/dashboard (chart configs)
│   │   │   ├── generate.py          ← POST /api/generate (full LLM report)
│   │   │   └── chat.py              ← POST /api/chat (grounded Q&A)
│   │   ├── visualization/
│   │   │   └── chart_selector.py    ← Recommends 8–15 chart configs (no LLM)
│   │   ├── rag/                     ← ChromaDB indexing, embedding, retrieval
│   │   ├── cleaning/                ← Pandas data cleaning & statistics
│   │   └── main.py                  ← FastAPI app entry point
│   ├── chroma_db/                   ← Local vector store (auto-created)
│   ├── requirements.txt
│   └── README.md                    ← AI Service endpoint & pipeline reference
│
└── frontend/                        ← React + Vite SPA (port 5173)
    ├── src/
    │   ├── pages/
    │   │   ├── Upload.jsx            ← Two-phase upload + dataset history selector
    │   │   ├── DatasetDashboardPage.jsx ← Side-by-side Plotly chart grid (new tab)
    │   │   ├── Report.jsx            ← Generated AI report viewer
    │   │   ├── History.jsx           ← User report history list
    │   │   └── Login.jsx / Register.jsx
    │   ├── services/
    │   │   ├── upload.js             ← Upload & getUploadedDatasets()
    │   │   ├── report.js             ← generateReport() & getDashboard()
    │   │   └── auth.js               ← Login, register, logout
    │   ├── routes/
    │   │   └── AppRoute.jsx          ← React Router v6 route definitions
    │   └── main.jsx
    ├── package.json
    └── README.md                    ← Frontend tech stack & routing reference
```

---

## ⚡ Core Workflows

### Phase 1 — Visual Profiling (No LLM · Instant · Free)

```
User picks file (new upload or from DB history)
              │
              ▼
     Backend fetches binary from MySQL
              │
              ▼
     AI Service: Pandas cleaning & statistics
              │
              ▼
  chart_selector.py recommends 8–15 charts
  (iterates top 3 categorical + numerical cols)
              │
              ▼
   Plotly JSON configs returned to backend
              │
              ▼
Frontend opens /dashboard/view/:fileId in new tab
              │
              ▼
  Charts rendered side-by-side (2-col grid)
  via react-plotly.js (no page refresh lost)
```

### Phase 2 — AI Report Generation (RAG + Gemini)

```
User types natural-language prompt
              │
              ▼
  Backend forwards file + prompt to AI Service
              │
              ├──► Pandas: clean & split into row text chunks
              │               │
              │               ▼
              │    sentence-transformers: embed chunks
              │               │
              │               ▼
              │         ChromaDB: index vectors
              │               │
              │               ▼
              │    Retriever: top-k similarity search
              │               │
              │               ▼
              └──► Prompt Builder: stats + context + user query
                               │
                               ▼
                      Google Gemini API
                               │
                               ▼
                    Markdown → styled HTML report
                               │
                               ▼
              Backend saves report to MySQL → returns to frontend
```

---

## 🛠️ Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Frontend Framework** | React 19 (Vite) |
| **Frontend Styling** | Tailwind CSS v4 |
| **Charts** | react-plotly.js + plotly.js-basic-dist |
| **Routing** | React Router v6 |
| **Backend Framework** | FastAPI + Uvicorn |
| **Backend ORM** | SQLAlchemy + PyMySQL |
| **Database** | MySQL |
| **Authentication** | JWT (python-jose) |
| **AI Microservice** | FastAPI + Pandas + NumPy |
| **Embeddings** | sentence-transformers (`all-MiniLM-L6-v2`) |
| **Vector Store** | ChromaDB (local, file-based) |
| **LLM** | Google Gemini API (generativeai SDK) |

---

## 🚀 Setup & Installation

Run all three services concurrently in separate terminal windows.

### Prerequisites
- Python 3.10+
- Node.js 18+
- MySQL Server (local instance)
- A Google Gemini API key ([Get one free here](https://aistudio.google.com/app/apikey))

---

### Step 1 — Database Setup

Ensure MySQL is running and create the project database:
```sql
CREATE DATABASE insightai;
```

---

### Step 2 — Backend (port 8000)

```bash
cd backend
python -m venv venv

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

Create `backend/.env`:
```env
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/insightai
JWT_SECRET=your_strong_jwt_secret_here
AI_SERVICE_URL=http://localhost:8001
```

Start the server:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

### Step 3 — AI Service (port 8001)

```bash
cd ai-service
python -m venv venv

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

Create `ai-service/.env`:
```env
GEMINI_API_KEY=your_actual_google_gemini_api_key
CHROMA_DB_PATH=./chroma_db
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2
HOST=0.0.0.0
PORT=8001
LOG_LEVEL=INFO
```

Start the service:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

---

### Step 4 — Frontend (port 5173)

```bash
cd frontend
npm install
```

Create `frontend/.env`:
```env
VITE_API_URL=http://localhost:8000/api
```

Install chart dependencies:
```bash
npm install react-plotly.js plotly.js-basic-dist
```

Start the dev server:
```bash
npm run dev
```

Open **[http://localhost:5173](http://localhost:5173)** in your browser.

---

## 🌐 API Endpoint Summary

### Backend (`:8000`)

| Endpoint | Method | Description |
| :--- | :---: | :--- |
| `/api/auth/register` | `POST` | Register a new user |
| `/api/auth/login` | `POST` | Authenticate and receive JWT token |
| `/api/auth/me` | `GET` | Get current authenticated user profile |
| `/api/auth/logout` | `POST` | Log out (client clears token) |
| `/api/upload` | `POST` | Upload a new CSV/Excel dataset |
| `/api/upload` | `GET` | Retrieve list of all previously uploaded datasets |
| `/api/dashboard/stats` | `GET` | Aggregated usage metrics |
| `/api/dashboard/generate` | `POST` | Generate visual dashboard charts for a dataset |
| `/api/dashboard/generate/{file_id}` | `GET` | Fetch charts by file ID (supports tab refresh) |
| `/api/report/generate` | `POST` | Generate full AI report via RAG + Gemini |
| `/api/report/{report_id}` | `GET` | Retrieve a saved report |
| `/api/report/{report_id}/download` | `GET` | Download report as HTML |
| `/api/history` | `GET` | Get user's report history |

### AI Microservice (`:8001`)

| Endpoint | Method | Description |
| :--- | :---: | :--- |
| `/health` | `GET` | Service health check |
| `/api/dashboard` | `POST` | Clean data + recommend Plotly chart configs |
| `/api/generate` | `POST` | Full RAG pipeline + Gemini report generation |
| `/api/chat` | `POST` | Grounded Q&A against a vectorised dataset |

---

## 🔒 Security & Privacy

- All data processing (cleaning, embeddings, ChromaDB) happens **100% locally** on your machine.
- MySQL and ChromaDB never leave your host system.
- The **only external call** is to the Google Gemini API during Phase 2 report generation, sending only prompt-relevant metadata snippets — no raw data files.
- JWT tokens are used for all authenticated routes, never stored server-side.

---

## 📖 Further Reading

- [Backend README](./backend/README.md) — Full API endpoint reference
- [AI Service README](./ai-service/README.md) — Local setup, pipeline diagrams, and endpoint testing guide
- [Frontend README](./frontend/README.md) — Tech stack, routing table, and component overview