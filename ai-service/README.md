# InsightAI - AI Service Setup & Testing Guide

The **AI Service** is a FastAPI-based microservice that handles dataset ingestion, cleaning, statistics computation, automatic Plotly visualization generation, vector store indexing (RAG via ChromaDB), and LLM detailed analysis (via Google Gemini API).

---

## 1. Prerequisites

Ensure you have the following installed on your machine:
* Python 3.10 or higher
* `pip` (Python package manager)

---

## 2. Local Environment Setup

Follow these steps to configure and run the service locally:

### Step A: Create a Virtual Environment
Move into the `ai-service` folder:
```bash
cd ai-service
```

Create a virtual environment:
```bash
python -m venv venv
```

Activate the virtual environment:
* **Windows (PowerShell)**:
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
* **Windows (CMD)**:
  ```cmd
  .\venv\Scripts\activate.bat
  ```
* **macOS / Linux**:
  ```bash
  source venv/bin/activate
  ```

### Step B: Install Dependencies
Install all required libraries from the `requirements.txt` file:
```bash
pip install -r requirements.txt
```

### Step C: Configure Environment Variables
Create a file named `.env` in the root of the `ai-service/` directory and configure the variables:
```env
# Google Gemini API credentials (Required for LLM features)
GEMINI_API_KEY=your_actual_gemini_api_key_here

# Directory path to store local ChromaDB database files
CHROMA_DB_PATH=./chroma_db

# Local embedding model ID from sentence-transformers library
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2

# Server host binding & port configuration
HOST=0.0.0.0
PORT=8001

# Logging details verbosity
LOG_LEVEL=INFO
```

---

## 3. Running the AI Service

Start the application server using Uvicorn:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

* **Interactive Swagger Documentation**: Once the service is running, navigate to [http://localhost:8001/docs](http://localhost:8001/docs) in your browser to inspect and test all API endpoints interactively.

---

## 4. Verifying Endpoints

Below are commands to test and verify the endpoints from the console (using PowerShell or curl).

### Endpoint 1: Health Check (GET `/health`)
Verifies if the AI Service is online.

* **PowerShell**:
  ```powershell
  Invoke-RestMethod -Uri "http://localhost:8001/health" -Method Get
  ```
* **cURL**:
  ```bash
  curl -X GET "http://localhost:8001/health"
  ```
* **Expected Response**:
  ```json
  {"status": "ok", "version": "1.0.0"}
  ```

### Endpoint 2: Non-LLM Dashboard Processing (POST `/api/dashboard`)
Accepts a dataset file upload and returns data cleaning status, statistics, and Plotly graph configurations.

* **PowerShell**:
  ```powershell
  Invoke-RestMethod -Uri "http://localhost:8001/api/dashboard" -Method Post -Form @{
      file = Get-Item "path_to_your_dataset.csv"
  }
  ```
* **cURL**:
  ```bash
  curl -X POST "http://localhost:8001/api/dashboard" -F "file=@path_to_your_dataset.csv"
  ```

### Endpoint 3: Grounded Q&A Chat (POST `/api/chat`)
Performs a semantic vector query on the index of the dataset and prompts Gemini.

* **PowerShell**:
  ```powershell
  Invoke-RestMethod -Uri "http://localhost:8001/api/chat" -Method Post -ContentType "application/json" -Body '{"dataset_id": "your_dataset_filename.csv", "query": "Which product generated the highest sales?", "top_k": 5}'
  ```
* **cURL**:
  ```bash
  curl -X POST "http://localhost:8001/api/chat" -H "Content-Type: application/json" -d '{"dataset_id": "your_dataset_filename.csv", "query": "Which product generated the highest sales?", "top_k": 5}'
  ```

### Endpoint 4: Full Report Generation (POST `/api/generate`)
Called by the backend to compile a complete analytics report.

* **PowerShell**:
  ```powershell
  Invoke-RestMethod -Uri "http://localhost:8001/api/generate" -Method Post -Form @{
      file = Get-Item "path_to_your_dataset.csv"
      prompt = "Generate a sales summary report and show regional performance."
  }
  ```
* **cURL**:
  ```bash
  curl -X POST "http://localhost:8001/api/generate" -F "file=@path_to_your_dataset.csv" -F "prompt=Generate a sales summary report and show regional performance."
  ```
* **Expected Response**:
  ```json
  {
      "report_title": "...",
      "summary": "...",
      "content": "<!-- Beautiful HTML Content -->",
      "statistics": { ... },
      "charts": [ ... ]
  }
  ```

Complete workflow 
CSV

↓

Pandas

↓

Statistics

↓

Embeddings

↓

ChromaDB

↓

User Prompt

↓

Retriever

↓

Relevant Rows

↓

Prompt Builder

↓

One Large Prompt

↓

Gemini

↓

Markdown Report

↓

HTML/PDF Generator





CSV/Excel
      │
      ▼
Pandas DataFrame
      │
      ▼
convert_dataframe_to_text_chunks()
      │
      ▼
List of Text Chunks
      │
      ▼
Embedding Model
      │
      ▼
Vectors
      │
      ▼
ChromaDB