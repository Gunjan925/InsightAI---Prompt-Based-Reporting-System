# InsightAI Backend API Reference

Below is the complete routing guide for the InsightAI Fastapi backend services:

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| **Authentication** | | |
| `/api/auth/register` | `POST` | Registers a new user with a unique username, email, and password. |
| `/api/auth/login` | `POST` | Authenticates the user and returns a JWT access token. |
| `/api/auth/me` | `GET` | Retrieves the profile details of the currently authenticated user. |
| `/api/auth/logout` | `POST` | Logs out the current user (client-side clears stored tokens). |
| **Dataset Uploads** | | |
| `/api/upload` | `POST` | Uploads a CSV or Excel dataset, validates structure/size, and stores it in MySQL. |
| `/api/upload` | `GET` | Retrieves all datasets previously uploaded by the authenticated user. |
| **Visual Dashboard (Phase 1)** | | |
| `/api/dashboard/stats` | `GET` | Returns aggregated metrics (upload count, report count, type distributions). |
| `/api/dashboard/generate` | `POST` | Generates dashboard stats and recommended Plotly charts for a dataset body parameter. |
| `/api/dashboard/generate/{file_id}` | `GET` | Generates dashboard stats and Plotly charts using URL path variable (refreshable). |
| **AI Reports (Phase 2)** | | |
| `/api/report/generate` | `POST` | Triggers LLM analysis (Gemini) using RAG context and compiles a report document. |
| `/api/report/{report_id}` | `GET` | Retrieves the complete HTML analytical report configuration. |
| `/api/report/{report_id}/download` | `GET` | Downloads the generated analytical report as a self-contained HTML page. |
| **History Overview** | | |
| `/api/history` | `GET` | Returns the authenticated user's previously generated reports. |