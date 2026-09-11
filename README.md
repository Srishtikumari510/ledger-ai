LedgerAI — Document Intelligence Platform
Turn complex financial documents into structured, validated intelligence.

An end-to-end AI-powered document extraction, validation, and API platform for financial documents — Invoices, Balance Sheets, Profit & Loss, and Cash Flow Statements.

https://img.shields.io/badge/Live%2520Demo-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white
https://img.shields.io/badge/API%2520Docs-Swagger-85EA2D?style=for-the-badge&logo=swagger&logoColor=black
https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github&logoColor=white
https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white
https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white

📋 Table of Contents
Overview

Live URLs

Architecture

Technology Stack

Local Setup

Environment Variables

API Reference

Financial Validation Rules

Persistence

Testing

Sample Outputs

Known Limitations

Production Improvements

AI / Tool Usage Declaration

Project Structure

Author

🎯 Overview
LedgerAI accepts financial documents as PDF / JPG / PNG, validates them, extracts every meaningful field and table using OCR + LLM, runs deterministic financial validations, persists the result, and serves it back through a consistent REST API and a Jinja2 dashboard.

The project demonstrates practical AI engineering: turning OCR + LLM capabilities into a reliable, structured, testable, and deployable application.

✨ Key Features
📄 Multi-format intake — PDF, JPG, PNG with file validation

🔍 Hybrid extraction — native PDF text + Tesseract OCR fallback

🤖 LLM-powered field extraction — Google Gemini with strict JSON schema & page-level evidence

✅ Deterministic financial validation — formula-based checks per document type

💾 Persistent storage — SQLAlchemy + SQLite (Postgres-ready)

🌐 Consistent REST API — auto-generated Swagger/OpenAPI docs

📊 Jinja2 dashboard — zero build step, fast, clean UI

🌐 Live URLs
Service	URL
Landing Page	https://ledger-ai-y8ff.onrender.com/
Dashboard	https://ledger-ai-y8ff.onrender.com/dashboard
API Base	https://ledger-ai-y8ff.onrender.com/api/v1
Health Check	https://ledger-ai-y8ff.onrender.com/api/v1/health
Swagger / OpenAPI	https://ledger-ai-y8ff.onrender.com/docs
GitHub Repo	https://github.com/Srishtikumari510/ledger-ai
⚠️ Note: The Render free tier puts services to sleep after ~15 minutes of inactivity. The first request may take 30–60 seconds to wake the service. This also means the SQLite database resets on cold start — processed documents are not retained after sleep. This is a known limitation of the free tier and does not affect correctness.

🏗️ Architecture
text
┌─────────────────────────────────────────┐
│           Browser / API Client          │
└────────────────────┬────────────────────┘
                     │ multipart/form-data + document_type
                     ▼
┌─────────────────────────────────────────┐
│          FastAPI  /api/v1               │  ← routes/documents.py
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│          Document Service               │  ← orchestrator
└────────────────────┬────────────────────┘
                     │
        ┌────────────┼────────────┬────────────┐
        ▼            ▼            ▼            ▼
   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌──────────────┐
   │  File   │  │   OCR   │  │   LLM   │  │  Financial   │
   │ Valida- │  │ Service │  │ Extrac- │  │  Validation  │
   │  tion   │  │         │  │  tion   │  │              │
   └─────────┘  └─────────┘  └─────────┘  └──────────────┘
                     │
                     ▼
         ┌────────────────────────┐
         │  Repository / SQLite   │  ← SQLAlchemy (Postgres-ready)
         └────────────────────────┘
🔄 Flow per Document
Validate — file type, size, readability, page count (≤ 3)

Extract text — native PDF text via pdfplumber, fallback to Tesseract OCR

Extract fields — LLM (Gemini) with strict JSON schema + page-level evidence

Validate financials — deterministic rules per document type

Persist — write JSON result to DB

Respond — return consistent structured JSON

🛠️ Technology Stack
Layer	Choice	Why
Web Framework	FastAPI	Auto-generated Swagger, async, Pydantic validation, great DX
Schemas	Pydantic v2	Structured typing, automatic validation, JSON serialization
Database	SQLAlchemy + SQLite	Zero-config dev; swap DATABASE_URL for Postgres in prod
OCR	Tesseract 5.x	Free, offline, mature, good enough for financial scans
PDF → Image	pdf2image + Poppler	Reliable scanned-PDF handling
PDF Text	pdfplumber	Best native text extraction quality on financial layouts
LLM	Google Gemini	Free tier, structured JSON output, low latency
Frontend	Jinja2 + vanilla HTML/CSS/JS	Zero build step; fast
Deployment	Render (Docker)	Free tier, Docker support, easy env-var config
💻 Local Setup
Prerequisites
Python 3.12

Tesseract OCR (system package)

Poppler (for pdf2image)

🪟 Windows
powershell
# Install external tools (once)
winget install UB-Mannheim.TesseractOCR
winget install oschwartz10612.Poppler

# Clone and set up
git clone https://github.com/Srishtikumari510/ledger-ai.git
cd ledger-ai/backend
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Configure
Copy-Item .env.example .env
notepad .env   # set LLM_API_KEY

# Run
uvicorn app.main:app --reload --port 8000
🐧 Linux / macOS
bash
# Install external tools (once)
sudo apt-get install -y tesseract-ocr poppler-utils      # Debian/Ubuntu
# or: brew install tesseract poppler                     # macOS

# Clone and set up
git clone https://github.com/Srishtikumari510/ledger-ai.git
cd ledger-ai/backend
python3.12 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# edit .env with your LLM_API_KEY

# Run
uvicorn app.main:app --reload --port 8000
🌍 Open in Browser
Service	URL
Landing	http://127.0.0.1:8000/
Dashboard	http://127.0.0.1:8000/dashboard
Swagger	http://127.0.0.1:8000/docs
⚙️ Environment Variables
See backend/.env.example:

env
APP_NAME=Document Intelligence API
APP_VERSION=1.0.0
LOG_LEVEL=INFO

DATABASE_URL=sqlite:///./documents.db

MAX_PAGES=3
MAX_FILE_SIZE_MB=20
UPLOAD_DIR=./uploads

LLM_PROVIDER=gemini
LLM_API_KEY=your_api_key_here
LLM_MODEL=gemini-2.5-flash

OCR_PROVIDER=tesseract
OCR_SPACE_API_KEY=
POPPLER_PATH=
🔐 Never commit .env. It is excluded by .gitignore.

🔑 Get a free Gemini key: https://aistudio.google.com/app/apikey

📡 API Reference
All endpoints are documented at /docs (Swagger UI).

POST /api/v1/documents/process
Upload and process a document.

bash
curl -X POST "https://ledger-ai-y8ff.onrender.com/api/v1/documents/process" \
  -F "file=@sample_invoice.pdf" \
  -F "document_type=invoice"
document_type must be one of:
invoice | balance_sheet | profit_and_loss | cash_flow_statement

GET /api/v1/documents/{document_name}
Retrieve the latest structured result by exact file name.

bash
curl "https://ledger-ai-y8ff.onrender.com/api/v1/documents/sample_invoice.pdf"
GET /api/v1/documents
List all processed documents (used by the dashboard).

bash
curl "https://ledger-ai-y8ff.onrender.com/api/v1/documents"
GET /api/v1/health
bash
curl "https://ledger-ai-y8ff.onrender.com/api/v1/health"
# → {"status":"ok","service":"Document Intelligence API","version":"1.0.0"}
📦 Response Shape (abridged)
json
{
  "document_name": "sample_invoice.pdf",
  "document_type": "invoice",
  "processing_status": "PASS",
  "file_validation": { "file_type": "application/pdf", "page_count": 1, "status": "PASS" },
  "extracted_data": {
    "invoice_number": { "value": "INV-2026-0042", "page_number": 1 },
    "total_amount":   { "value": 2783.00, "page_number": 1 },
    "line_items": [
      { "description": "Office Chair", "quantity": 5, "unit_price": 120, "amount": 600 }
    ]
  },
  "validation": {
    "overall_status": "PASS",
    "checks": [
      {
        "name": "invoice_total_check",
        "formula": "subtotal + tax - discount",
        "calculated_value": 2783.0,
        "reported_value": 2783.0,
        "variance": 0.0,
        "status": "PASS"
      }
    ]
  },
  "processing_metadata": {
    "ocr_used": false,
    "llm_used": true,
    "llm_provider": "gemini",
    "llm_model": "gemini-2.5-flash",
    "processed_at": "2026-09-11T12:00:00Z",
    "processing_time_ms": 2840
  }
}
❌ Error Response Shape
json
{
  "error": {
    "code": "UNSUPPORTED_FILE_TYPE",
    "message": "Only PDF / JPG / PNG documents are supported."
  }
}
✅ Financial Validation Rules
Rules are deterministic. Each check returns the formula used, operands, calculated value, reported value, variance, and a status (PASS / FAILED / NOT_APPLICABLE).

Document	Check
Invoice	quantity × unit_price ≈ line amount (per line)
Invoice	subtotal + tax_amount − discount ≈ total_amount
Invoice	sum(line_items.amount) ≈ subtotal
Balance Sheet	total_liabilities + total_equity ≈ total_assets
Balance Sheet	sum(asset components) ≈ reported total_assets (per period)
P&L	revenue − cost_of_sales ≈ gross_profit
P&L	gross_profit − operating_expenses ≈ operating_profit
P&L	operating_profit − tax ≈ net_profit
Cash Flow	operating + investing + financing ≈ net_change_in_cash
Cash Flow	opening_cash + net_change_in_cash ≈ closing_cash
📏 Tolerance: max(0.01, 0.001 × |reported|). Parenthesized numbers (e.g. (1,234)) are treated as negative. Per-period checks run independently for each comparative year.

🚫 If a required operand is missing, the check returns NOT_APPLICABLE — values are never invented.

💾 Persistence
Model: backend/app/models/document.py (SQLAlchemy)

Repository: backend/app/repositories/document_repository.py

Dev DB: SQLite (backend/documents.db)

Prod-ready: swap DATABASE_URL to postgresql+psycopg2://... — same code path

Each processed document is stored as a row with:
document_name, document_type, processing_status, overall_confidence, file_validation (JSON), extracted_data (JSON), validation (JSON), processing_metadata (JSON), created_at.

GET /api/v1/documents/{name} returns the most recent row for that name.

🧪 Testing
bash
cd backend
pytest -v
Covers:

✅ File validation (type, size, page count, corrupted file)

✅ Financial validation rules (invoice, balance sheet, P&L, cash flow)

✅ API flow (health, process, get-by-name, list)

📂 Sample Outputs
See sample_outputs/ for JSON responses from real documents:

invoice.json

balance_sheet.json

profit_and_loss.json

cash_flow_statement.json

failure_no_text.json (documented NO_TEXT_EXTRACTED case)

⚠️ Known Limitations
🔄 Free-tier deployment resets the DB on service sleep (Render). Use a persistent Postgres or a paid instance for retention.

🖨️ OCR quality depends on scan quality. Very low-DPI or skewed pages may return NO_TEXT_EXTRACTED.

🤖 LLM extraction is best-effort. Occasionally a field is captured under a synonym or missed; validation catches material inconsistencies.

⏱️ Free-tier request timeout on Render is ~100s. Very large multi-page documents may need a paid tier or async processing.

🌐 English-only OCR and prompt.

🔓 No authentication on the API — intended as a technical demonstration.

🚀 Production Improvements
Persistent Postgres + connection pooling (already DB-agnostic)

Async job queue (Celery / RQ) for documents > 2 pages; return 202 Accepted with a job ID

Object storage (S3) instead of ephemeral disk for original files

Auth — API keys / OAuth2 + per-tenant rate limits

Confidence scoring — combine OCR confidence + LLM logprobs into a calibrated per-field score

Redaction — PII stripping before external LLM calls

Observability — OpenTelemetry traces, structured JSON logs, error tracking (Sentry)

Schema versioning — version the response envelope for backward compatibility

Golden test set with per-field precision/recall dashboards

🤖 AI / Tool Usage Declaration
LLMs used in the product: Google Gemini (gemini-2.5-flash) for field and table extraction with a strict JSON schema and page-level evidence.

AI coding assistants used during development for scaffolding, prompt iteration, and debugging (error triage, Windows/PowerShell friction, Pydantic edge cases).

All financial validation logic is deterministic and hand-written — the LLM is only used for structured extraction.

No sample outputs are hardcoded. Extraction runs live against uploaded files.

📁 Project Structure
text
project-root/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/routes/documents.py
│   │   ├── core/{config,database,logging}.py
│   │   ├── models/document.py
│   │   ├── schemas/{document,extraction}.py
│   │   ├── services/
│   │   │   ├── document_validation_service.py
│   │   │   ├── ocr_service.py
│   │   │   ├── extraction_service.py
│   │   │   ├── financial_validation_service.py
│   │   │   └── document_service.py
│   │   ├── repositories/document_repository.py
│   │   └── utils/
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── templates/{landing,dashboard,document_result}.html
│   └── static/{css,js}/
├── docs/
│   └── architecture.png
├── sample_outputs/
├── Dockerfile
├── .dockerignore
├── .env.example
├── .gitignore
└── README.md
👩‍💻 Author
Srishti Kumari

https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white
https://img.shields.io/badge/GitHub-Follow-181717?style=for-the-badge&logo=github&logoColor=white

⭐ If you find this project useful, consider giving it a star on GitHub!

Built with FastAPI, Google Gemini, and a lot of deterministic validation.
