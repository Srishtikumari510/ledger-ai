LedgerAI — Document Intelligence Platform

An end-to-end AI-powered document extraction, validation, and API platform for financial documents.



https://img.shields.io/badge/Live-Demo-brightgreen

https://img.shields.io/badge/API-Swagger-blue

https://img.shields.io/badge/GitHub-Repository-black



Live Demo: https://ledger-ai-y8ff.onrender.com/

API Base: https://ledger-ai-y8ff.onrender.com/api/v1

Swagger/OpenAPI: https://ledger-ai-y8ff.onrender.com/docs

Health Check: https://ledger-ai-y8ff.onrender.com/api/v1/health

GitHub: https://github.com/Srishtikumari510/ledger-ai



Table of Contents

Overview



Supported Document Types



Key Features



Architecture



Processing Flow



Technology Stack



Local Setup



Environment Variables



API Reference



Project Structure



Validation Engine



Deployment



Roadmap



Contributing



License



Overview

Financial-services teams receive invoices and financial statements as native or scanned PDF / JPG / PNG files. Different layouts, poor scan quality, and OCR noise make manual extraction slow, error-prone, and inconsistent.



LedgerAI solves this by combining OCR, LLM-based field extraction, and deterministic financial validation into a single API. Upload a document, get back structured JSON — with page-level evidence and formula-level validation for every number.



Supported Document Types

Document Type	Extracted Fields

Invoice	invoice\_number, vendor, customer, currency, subtotal, tax, discount, total, line items

Balance Sheet	assets, liabilities, equity, line items, per-period

Profit \& Loss	revenue, COGS, gross profit, operating expenses, tax, net profit

Cash Flow Statement	operating / investing / financing cash flows, opening \& closing cash

Every extracted value carries:



Page number — where it was found



Source evidence — the raw text snippet used



Every financial relationship is validated with:



Formula — e.g. subtotal + tax - discount = total



Operands — the values plugged in



Calculated value vs Reported value



Variance and Status (PASS / FAIL / NOT\_APPLICABLE)



Key Features

📄 Multi-format ingestion — native PDF, scanned PDF, JPG, PNG



🔍 Hybrid text extraction — pdfplumber for native text, Tesseract OCR fallback



🤖 LLM-powered field extraction — Gemini with strict JSON schema enforcement



✅ Deterministic financial validation — explicit formulas, operands, variance, status



🧾 Page-level evidence — every value traceable to its source



🗄️ Persistent results — SQLAlchemy + SQLite (Postgres-ready)



⚡ FastAPI — async, auto-generated Swagger, Pydantic v2 validation



🐳 Docker-ready — one-command deploy to Render



Architecture

text

┌─────────────────────┐

│   Browser / API     │

└──────────┬──────────┘

&#x20;          │ multipart/form-data + document\_type

&#x20;          ▼

┌─────────────────────┐

│  FastAPI /api/v1    │  ← routes/documents.py

└──────────┬──────────┘

&#x20;          │

&#x20;          ▼

┌─────────────────────┐

│  Document Service   │  orchestrator

└──────────┬──────────┘

&#x20;          │

&#x20;  ┌───────┼─────────┬────────────┐

&#x20;  ▼       ▼         ▼            ▼

┌───────┐ ┌───────┐ ┌────────┐ ┌──────────┐

│ File  │ │ OCR   │ │  LLM   │ │ Financial│

│ Vali- │ │ Serv- │ │ Extrac-│ │ Valida-  │

│ dation│ │ ice   │ │ tion   │ │ tion     │

└───────┘ └───────┘ └────────┘ └──────────┘

&#x20;          │

&#x20;          ▼

&#x20;  ┌────────────────┐

&#x20;  │  Repository /  │  SQLAlchemy

&#x20;  │  SQLite (PG)   │

&#x20;  └────────────────┘

Processing Flow

Validate — file type, size, readability, page count (≤ 3)



Extract text — native PDF text via pdfplumber, fallback to Tesseract OCR



Extract fields — LLM (Gemini) with strict JSON schema + page-level evidence



Validate financials — deterministic rules per document type



Persist — write JSON result to DB



Respond — return consistent structured JSON



Technology Stack

Layer	Choice	Why

Web framework	FastAPI	Auto-generated Swagger, async, Pydantic validation, great DX

Schemas	Pydantic v2	Structured typing, automatic validation, JSON serialization

Database	SQLAlchemy + SQLite	Zero-config dev; swap DATABASE\_URL for Postgres in prod

OCR	Tesseract 5.x	Free, offline, mature, good enough for financial scans

PDF → image	pdf2image + Poppler	Reliable scanned-PDF handling

PDF text	pdfplumber	Best native text extraction quality on financial layouts

LLM	Google Gemini	Free tier, structured JSON output, low latency

Frontend	Jinja2 + vanilla HTML/CSS/JS	Zero build step; fast

Deployment	Render (Docker)	Free tier, Docker support, easy env-var config

Local Setup

Prerequisites

Python 3.12



Tesseract OCR (system package)



Poppler (for pdf2image)



Windows

powershell

\# Install external tools (once)

winget install UB-Mannheim.TesseractOCR

winget install oschwartz10612.Poppler



\# Clone and set up

git clone https://github.com/Srishtikumari510/ledger-ai.git

cd ledger-ai/backend

py -3.12 -m venv venv

.\\venv\\Scripts\\Activate.ps1

pip install -r requirements.txt



\# Configure

Copy-Item .env.example .env

notepad .env   # set LLM\_API\_KEY



\# Run

uvicorn app.main:app --reload --port 8000

macOS

bash

\# Install external tools (once)

brew install tesseract poppler



\# Clone and set up

git clone https://github.com/Srishtikumari510/ledger-ai.git

cd ledger-ai/backend

python3.12 -m venv venv

source venv/bin/activate

pip install -r requirements.txt



\# Configure

cp .env.example .env

nano .env   # set LLM\_API\_KEY



\# Run

uvicorn app.main:app --reload --port 8000

Linux (Debian / Ubuntu)

bash

\# Install external tools (once)

sudo apt-get update

sudo apt-get install -y tesseract-ocr poppler-utils



\# Clone and set up

git clone https://github.com/Srishtikumari510/ledger-ai.git

cd ledger-ai/backend

python3.12 -m venv venv

source venv/bin/activate

pip install -r requirements.txt



\# Configure

cp .env.example .env

nano .env   # set LLM\_API\_KEY



\# Run

uvicorn app.main:app --reload --port 8000

Once running, open:



App: http://localhost:8000



Swagger: http://localhost:8000/docs



Health: http://localhost:8000/api/v1/health



Environment Variables

Create a .env file in backend/:



Variable	Description	Example

LLM\_API\_KEY	Google Gemini API key	AIza...

LLM\_MODEL	Gemini model name	gemini-1.5-flash

DATABASE\_URL	SQLAlchemy connection string	sqlite:///./ledger.db

MAX\_FILE\_SIZE\_MB	Upload size limit	10

MAX\_PAGES	Max pages per document	3

TESSERACT\_CMD	Path to Tesseract binary (Windows only)	C:\\Program Files\\Tesseract-OCR\\tesseract.exe

API Reference

POST /api/v1/documents/extract

Upload a document and receive structured JSON.



Request — multipart/form-data



Field	Type	Required	Description

file	file	✅	PDF / JPG / PNG (≤ 3 pages, ≤ 10 MB)

document\_type	string	✅	invoice | balance\_sheet | profit\_loss | cash\_flow

Example



bash

curl -X POST https://ledger-ai-y8ff.onrender.com/api/v1/documents/extract \\

&#x20; -F "file=@invoice.pdf" \\

&#x20; -F "document\_type=invoice"

Response (abridged)



json

{

&#x20; "document\_id": "b1f2c3...",

&#x20; "document\_type": "invoice",

&#x20; "status": "success",

&#x20; "extracted": {

&#x20;   "invoice\_number": { "value": "INV-2041", "page": 1, "evidence": "Invoice No: INV-2041" },

&#x20;   "vendor":         { "value": "Acme Corp", "page": 1, "evidence": "From: Acme Corp" },

&#x20;   "subtotal":       { "value": 1000.00,   "page": 1, "evidence": "Subtotal 1000.00" },

&#x20;   "tax":            { "value": 180.00,    "page": 1, "evidence": "GST 18% 180.00" },

&#x20;   "total":          { "value": 1180.00,   "page": 1, "evidence": "Total 1180.00" }

&#x20; },

&#x20; "validations": \[

&#x20;   {

&#x20;     "rule": "subtotal + tax - discount = total",

&#x20;     "operands": { "subtotal": 1000.00, "tax": 180.00, "discount": 0.00 },

&#x20;     "calculated": 1180.00,

&#x20;     "reported": 1180.00,

&#x20;     "variance": 0.00,

&#x20;     "status": "PASS"

&#x20;   }

&#x20; ]

}

GET /api/v1/health

Returns service health and dependency status.



GET /docs

Interactive Swagger UI for all endpoints.



Project Structure

text

ledger-ai/

├── backend/

│   ├── app/

│   │   ├── main.py                 # FastAPI entrypoint

│   │   ├── routes/

│   │   │   └── documents.py        # /api/v1/documents endpoints

│   │   ├── services/

│   │   │   ├── document\_service.py # orchestrator

│   │   │   ├── ocr\_service.py      # Tesseract + pdfplumber

│   │   │   ├── llm\_service.py      # Gemini extraction

│   │   │   └── validation\_service.py

│   │   ├── schemas/                # Pydantic v2 models

│   │   ├── models/                 # SQLAlchemy models

│   │   ├── repository/             # DB access layer

│   │   └── templates/              # Jinja2 frontend

│   ├── requirements.txt

│   ├── Dockerfile

│   └── .env.example

└── README.md

Validation Engine

Each document type has its own rule set. Example rules:



Invoice



subtotal + tax − discount = total



Σ(line\_items.amount) = subtotal



Balance Sheet



assets = liabilities + equity



Σ(line\_items) = section total (per period)



Profit \& Loss



revenue − COGS = gross\_profit



gross\_profit − opex − tax = net\_profit



Cash Flow



operating + investing + financing = net\_change



opening\_cash + net\_change = closing\_cash



Every result reports PASS, FAIL, or NOT\_APPLICABLE with full operands and variance.



Deployment

Deployed on Render via Docker.



Push your fork to GitHub



Create a new Web Service on Render → Docker



Set root directory to backend/



Add environment variables (LLM\_API\_KEY, DATABASE\_URL, etc.)



Deploy — Render builds the Dockerfile and exposes port 8000



For production Postgres, set:



text

DATABASE\_URL=postgresql+psycopg2://user:pass@host:5432/ledger

Roadmap

□ Multi-page support beyond 3 pages

□ Additional document types (receipts, bank statements, tax forms)

□ Async job queue for large batches

□ Per-tenant API keys and rate limiting

□ Export to CSV / Excel

□ Human-in-the-loop review UI

Contributing

Fork the repo



Create a feature branch: git checkout -b feat/your-feature



Commit: git commit -m "feat: add your feature"



Push: git push origin feat/your-feature



Open a Pull Request



License

MIT — see LICENSE for details.



Built by Srishti Kumari · Powered by FastAPI, Gemini, Tesseract, and SQLAlchemy.

