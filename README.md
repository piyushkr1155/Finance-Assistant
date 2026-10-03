# LocalLedger AI

> **An open-source, local-first financial intelligence assistant for small businesses.**  
> Ingests bank statements and spreadsheets, executes 100% deterministic mathematical calculations, and provides grounded executive briefings and interactive Q&A using local open-weight AI via Ollama. **Zero cloud data exfiltration.**

[![Hacktoberfest 2026](https://img.shields.io/badge/Hacktoberfest-2026-ff7a00.svg)](https://hacktoberfest.com/)
[![DEV Challenge](https://img.shields.io/badge/DEV_Challenge-%231_Open_Source-0a0a0a.svg?logo=dev.to)](https://dev.to)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.13](https://img.shields.io/badge/Python-3.13+-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.141+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js 16](https://img.shields.io/badge/Next.js-16_Turbopack-black.svg?logo=next.js&logoColor=white)](https://nextjs.org)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-4.0-38B2AC.svg?logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![Ollama Local AI](https://img.shields.io/badge/Ollama-Local_AI-white.svg?logo=ollama&logoColor=black)](https://ollama.com)
[![Tests Passing](https://img.shields.io/badge/Tests-54_Passed-success.svg?logo=pytest&logoColor=white)](backend/tests/)

---

## 📌 The Problem

Small business owners, independent consultants, and bootstrapped startups generate bank statements, invoice exports, and accounting spreadsheets every month. Yet, they face a painful dilemma:

1. **The Cloud AI Privacy Hazard**: Uploading confidential client names, payroll disbursements, vendor invoices, and margins to public cloud AI APIs (OpenAI, Anthropic, Google) risks data leaks, regulatory exposure, and unauthorized training on private financial data.
2. **The Math Hallucination Trap**: Large Language Models are probabilistic text generators, not calculators. When asked to compute totals or cash flow margins, LLMs frequently hallucinate numbers, miscalculate sums, or invent nonexistent discrepancies.
3. **The Data Analyst Void**: Most small businesses cannot afford a dedicated financial analyst or fractional CFO to parse complex spreadsheets and extract actionable monthly cash flow intelligence.

---

## 💡 The Solution: LocalLedger AI

**LocalLedger AI** is an open-source, private-by-design financial intelligence workspace. It bridges deterministic financial accounting with local artificial intelligence through a strict two-tier separation of concerns:

- **Tier 1: Deterministic Math Engine (Python)** — 100% of arithmetic calculations (Total Income, Total Expenses, Net Cash Flow, Savings Rate %, MoM Growth %, Category Allocations, and Outlier Bounds) are executed with exact mathematical precision in Python. **AI is never permitted to calculate or guess numbers.**
- **Tier 2: Grounded Local AI Reasoning (Ollama)** — An open-weight, locally hosted language model (`llama3.2:1b`, `qwen2.5:1.5b`, etc.) receives only certified mathematical facts and synthesizes plain-English executive briefings, explains unusual transactions, and answers business queries.

```
                      +------------------------------------------+
                      |       Confidential Ledger Ingestion      |
                      |          (CSV, XLSX, XLS <= 10MB)        |
                      +--------------------+---------------------+
                                           |
                                           v
                      +------------------------------------------+
                      |     Deterministic Data Processing        |
                      |   • Path Sanitization & RAM-only storage |
                      |   • Auto Column & Synonym Detection      |
                      |   • Dual Debit/Credit & Signed Normalizer|
                      +--------------------+---------------------+
                                           |
                                           v
                      +------------------------------------------+
                      |     Mathematical Analytics Engine        |
                      |   • Total Revenue & Expenditures         |
                      |   • Net Cash Flow & Operating Margin %   |
                      |   • Month-over-Month Growth Rates        |
                      |   • Leave-One-Out & IQR Anomaly Detection|
                      +--------------------+---------------------+
                                           |
                 +-------------------------+-------------------------+
                 |                                                   |
                 v                                                   v
   +---------------------------+                       +---------------------------+
   |  Visual Dashboard UI      |                       |  Context Builder & Guard  |
   |  • Next.js 16 Turbopack   |                       |  • Structured Facts Only  |
   |  • Recharts Visualizations|                       |  • Anti-Hallucination Gate|
   |  • Interactive Skeletons  |                       +-------------+-------------+
   +---------------------------+                                     |
                                                                     v
                                                       +---------------------------+
                                                       | Local Ollama Daemon       |
                                                       | (100% On-Device Offline)  |
                                                       | • llama3.2:1b / qwen2.5   |
                                                       +-------------+-------------+
                                                                     |
                                                                     v
                                                       +---------------------------+
                                                       | Fact-Checking Validator   |
                                                       | Cross-references output   |
                                                       | against certified metrics |
                                                       +---------------------------+
```

*For detailed Mermaid diagrams, trust boundaries, sequence diagrams, and performance benchmarks, view the full [System Architecture Documentation](docs/architecture.md).*

---

## ✨ Key Features

- 🔒 **100% On-Device Privacy**: No transaction details, customer names, or amounts ever leave your computer. Operates completely offline with local Ollama models.
- 🧮 **Zero Math Hallucinations**: Every single percentage, total, and balance is computed deterministically in Python before being presented or summarized.
- 📂 **Universal File Parsing**: Ingests `.csv`, `.xlsx`, and `.xls` files. Supports signed `Amount` columns, dual `Debit` & `Credit` columns, and custom column synonyms from global banks, QuickBooks, and Tally.
- 📊 **Executive Financial Dashboard**: Real-time KPI summary cards (Total Revenue, Total Expenditures, Net Cash Flow, and Retention / Savings Margin).
- 📈 **Cash Flow & Trend Analysis**: Visualizes monthly inflows and outflows with month-over-month percentage growth rates using interactive Recharts.
- 🥧 **Expense Breakdown**: Visual distribution of expenditures across operational categories with auto-categorization fallback.
- ⚠️ **Unusual Transaction Detection**: Statistical outlier detection combining Leave-One-Out category baseline comparison ($> 2.5\times$ variance), non-parametric Interquartile Range ($Q_3 + 1.5 \times \text{IQR}$), and monthly budget concentration.
- 🔍 **Interactive Inline "Explain with AI" Drawers**: Expand any detected anomaly to inspect a grounded, natural-language explanation of why it occurred and recommended next steps.
- 💬 **"Ask My Business" Grounded Q&A**: Natural language querying classified into financial intents with structured 4-card responses: Direct Answer, Certified Data Points, Why It Matters, and What to Check.
- 🗑️ **Ephemeral Session Purge**: One-click "Purge & Reset" button permanently clears active ledger data and memory from the server (`DELETE /api/session`).
- ⚡ **1-Click Realistic Demo Dataset**: Pre-loaded with 118 transactions spanning 6 months with 4 explainable real-world anomalies.

---

## 🏛️ System Architecture

### Component Hierarchy

```
LocalLedger AI
├── frontend/                     # Next.js 16 (App Router) + TypeScript
│   ├── app/                      # Layout, metadata, viewport, and page
│   ├── components/               # UI components
│   │   ├── Header.tsx            # Live AI pulse status & privacy modal
│   │   ├── UploadZone.tsx        # Drag-and-drop file ingestion & demo button
│   │   ├── KPICards.tsx          # Key metrics & margin status badges
│   │   ├── CashFlowChart.tsx     # Monthly bar chart with net overlay
│   │   ├── CategoryChart.tsx     # Expense distribution donut chart
│   │   ├── AIInsightsSection.tsx # Executive briefing with 1-click clipboard copy
│   │   ├── AskMyBusinessSection.tsx # Structured 4-part grounded Q&A
│   │   ├── AnomaliesSection.tsx  # Outliers with inline AI explanation drawers
│   │   ├── LargestExpensesSection.tsx # Top individual transactions
│   │   └── TransactionsTable.tsx # Searchable, filterable ledger table
│   ├── lib/api.ts                # Type-safe client communication
│   └── types/index.ts            # Shared TypeScript domain contracts
│
├── backend/                      # FastAPI Python Application
│   ├── api/                      # REST API routing
│   │   ├── upload.py             # File ingestion & column mapping
│   │   ├── analytics.py          # Summary, trends, categories, largest
│   │   └── ai.py                 # Status, insights, Q&A, explain-anomaly
│   ├── models/                   # Pydantic v2 schemas
│   ├── services/                 # Core deterministic & AI services
│   │   ├── file_parser.py        # CSV/Excel parsing & path traversal defense
│   │   ├── normalizer.py         # Column heuristics, date & currency cleansing
│   │   ├── analytics_engine.py   # High-precision deterministic metrics
│   │   ├── anomaly_detector.py   # O(N) Leave-One-Out & IQR outlier detection
│   │   ├── session_store.py      # RAM-only ephemeral storage & purge
│   │   ├── ai_provider.py        # Ollama local client & graceful degradation
│   │   ├── context_builder.py    # Structured facts payload generation
│   │   ├── prompt_templates.py   # Anti-hallucination system prompt rules
│   │   ├── ai_validator.py       # Number verification against certified facts
│   │   └── intent_router.py      # Query classification & 4-part synthesis
│   ├── tests/                    # Comprehensive Pytest Suite (54 tests)
│   └── main.py                   # FastAPI app & global 500 error handler
│
└── data/                         # Realistic small business demo datasets
    ├── sample_transactions.csv   # 118 transactions across 6 months
    ├── sample_transactions.xlsx  # Binary Excel workbook format
    └── generate_demo_data.py     # Reproducible synthetic generator
```

---

## 🛠️ Technology Stack

| Layer | Technologies | Justification |
| :--- | :--- | :--- |
| **Frontend** | **Next.js 16 (App Router)**, **TypeScript**, **Tailwind CSS 4.0** | Server-rendering speed, fast Turbopack compilation, strict type safety, modern sleek dark aesthetics |
| **Visualizations**| **Recharts**, **Lucide React** | Accessible, dynamic responsive charts and clear iconography |
| **Backend** | **FastAPI**, **Python 3.13**, **Pydantic v2** | High-performance asynchronous REST API with automatic OpenAPI documentation and strict data validation |
| **Data Engine** | **Pandas**, **NumPy**, **OpenPyXL** | Vectorized mathematical operations, high-speed aggregations, and robust Excel/CSV parsing |
| **Local AI Engine** | **Ollama**, **Llama 3.2 1B**, **Qwen 2.5 1.5B** | 100% on-device open-weight inference with zero telemetry and automatic model fallback |
| **Testing** | **Pytest**, **AnyIO**, **Starlette TestClient** | Rigorous automated testing across numerical precision, edge cases, error containment, and E2E lifecycle |

---

## 🛡️ Privacy & Security Architecture

> We believe small business owners deserve complete transparency regarding how their ledger data is handled. We do not make misleading claims of being "100% secure," but implement strict, verifiable technical protections to safeguard financial records:

1. **Local Inference Only**: Natural language synthesis is executed entirely on your machine via local Ollama models (`http://127.0.0.1:11434`). No transaction details, payee names, or financial summaries are transmitted to external cloud AI APIs.
2. **Ephemeral In-Memory Storage**: Uploaded files and normalized data exist only in server RAM for the duration of your session. Ledgers are **never** written to unencrypted databases, temporary hard drive swap files, or public web directories.
3. **One-Click Memory Purge**: Users can permanently erase all active session transactions and cached calculations from memory at any time with a single click or via `DELETE /api/session`. Subsequent requests immediately return HTTP 404.
4. **Hardened Ingestion**: File names are strictly sanitized (`sanitize_filename()`) to prevent directory traversal attacks (`../`, null bytes). Maximum upload payload is capped at 10 MB, and only `.csv`, `.xlsx`, and `.xls` extensions are accepted.
5. **Anti-Hallucination Grounding Gate**: The local LLM never sees raw, unstructured documents. It receives only pre-computed mathematical summaries, and AI responses are verified against ground-truth analytical numbers (with a 5% tolerance window for rounded figures).
6. **No Sensitive Logging**: Server logs deliberately omit transaction descriptions and amounts. No tracking beacons, analytics scripts, or cookies are present.

*Read the complete [Privacy & Security Technical Documentation](docs/privacy.md) for full audit details.*

---

## 📐 Mathematical Rigor & Formulas

All business analytics are calculated through deterministic algorithms:

| Metric | Formula | Edge Case Handling |
| :--- | :--- | :--- |
| **Total Income** | $\sum_{t \in \text{Income}} \text{Amount}_t$ | Handled as positive float; negative signs stripped if type is classified as income |
| **Total Expenses** | $\sum_{t \in \text{Expense}} \text{Amount}_t$ | Handled as positive magnitude; credit/debit column normalizer reconciles signs |
| **Net Cash Flow** | $\text{Total Income} - \text{Total Expenses}$ | Positive indicates Operating Surplus; negative indicates Operating Deficit |
| **Savings Rate (Net Margin %)** | $\left( \frac{\text{Net Cash Flow}}{\text{Total Income}} \right) \times 100$ | If $\text{Total Income} = 0$, rate defaults to `0.0%` to prevent division-by-zero crashes |
| **Month-over-Month Growth %** | $\left( \frac{\text{Current Month} - \text{Previous Month}}{\text{Previous Month}} \right) \times 100$ | First month returns `null`; if $\text{Previous Month} = 0$, returns `null` |
| **Category Allocation %** | $\left( \frac{\text{Category Expense}}{\text{Total Expenses}} \right) \times 100$ | Sum of all category percentages strictly verifies to $100.0\% \pm 0.1\%$ |
| **IQR Statistical Outlier** | $\text{Upper Bound} = Q_3 + 1.5 \times (Q_3 - Q_1)$ | Applied separately to income and expenses to avoid baseline distortion |
| **Leave-One-Out Category Variance**| $\text{Baseline} = \frac{\sum_{i \ne j} \text{Amount}_i}{N - 1}$ | Prevents an extreme purchase from inflating its own category reference mean |

---

## 📋 Prerequisites

- **Node.js**: v18.18+ or v20+ / v24+
- **Python**: 3.10+ (Tested on Python 3.13)
- **Ollama**: (Optional for natural language briefings and Q&A; core analytics and dashboard operate 100% independently without it)

---

## 🚀 Quick Start & Installation

### 1. Clone the Repository

```bash
git clone https://github.com/piyushkr1155/Finance-Assistant.git
cd Finance-Assistant
```

### 2. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv

# On Windows:
.\venv\Scripts\activate

# On Linux / macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the FastAPI server
python -m uvicorn main:app --reload --port 8000
```
*The backend API will be live at `http://127.0.0.1:8000` (Interactive Swagger docs at `http://127.0.0.1:8000/docs`).*

### 3. Frontend Setup

In a new terminal window:

```bash
cd frontend

# Install dependencies
npm install

# Start Next.js development server
npm run dev
```
*The frontend dashboard will be live at `http://localhost:3000`.*

### 4. Setup Local AI with Ollama (Optional)

To enable local AI executive summaries and interactive Q&A:

```bash
# 1. Download and install Ollama from https://ollama.com
# 2. Pull and start a lightweight open-weight model:
ollama run llama3.2:1b

# (Alternatively, for multilingual support or higher reasoning quality):
ollama run qwen2.5:1.5b
```
*Once running, refresh `http://localhost:3000`. The AI status indicator in the header will turn emerald, showing **"llama3.2:1b Ready"**.*

---

## 📊 Sample Dataset & Demo Guide

A realistic small business ledger spanning **6 months** (May to October 2026) with **118 transactions** is included out-of-the-box.

### Instant 1-Click Evaluation
1. Open `http://localhost:3000`.
2. Click the green button: **"Load Realistic Demo Dataset (1-Click)"**.
3. The dashboard will instantly populate all monthly cash flow charts, category breakdowns, and detected outliers.

### 4 Real-World Anomalies in the Demo Dataset
- 📅 **July 2026**: *AWS 1-Year Reserved Cloud Commitment Prepayment* (₹94,500 vs typical ₹4,500 monthly cloud spend).
- 📅 **August 2026**: *Apple Workstation & 4K Studio Displays Upgrade* (₹148,000 vs typical ₹3,000 monthly office spend).
- 📅 **September 2026**: *V2 Product Launch Multi-Channel Ad Blitz* (₹72,000 vs typical ₹15,000 monthly ad spend).
- 📅 **October 2026**: *Corporate IP Trademark & Annual Legal Retainer* (₹58,000 vs typical ₹8,000 monthly bookkeeping).

*Try clicking **"Explain with AI"** on any of these entries to see how LocalLedger AI delivers grounded business reasoning.*

---

## 📡 REST API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/upload` | Ingest CSV/Excel, detect columns, and return session ID & validation report |
| `POST` | `/api/upload/confirm-mapping` | Override or confirm custom column mappings for an active session |
| `GET` | `/api/transactions` | Retrieve normalized, paginated, searchable transactions list |
| `GET` | `/api/analytics/summary` | Retrieve summary KPIs (Income, Expenses, Net Cash Flow, Savings Rate) |
| `GET` | `/api/analytics/monthly` | Retrieve monthly aggregated totals and month-over-month growth rates |
| `GET` | `/api/analytics/categories` | Retrieve category breakdown with monetary values and percentages |
| `GET` | `/api/analytics/largest` | Retrieve highest-value transactions (filtered by expense or income) |
| `GET` | `/api/analytics/anomalies` | Retrieve statistical outliers flagged via Leave-One-Out and IQR rules |
| `GET` | `/api/ai/status` | Inspect local Ollama daemon connectivity and installed models |
| `POST` | `/api/ai/insights` | Generate natural-language executive briefing grounded in certified metrics |
| `POST` | `/api/ai/ask` | Natural language Q&A returning structured 4-part business answers |
| `POST` | `/api/ai/explain-anomaly`| Generate grounded explanation and next steps for a specific anomaly |
| `DELETE`| `/api/session` | Purge active ledger data and calculations completely from memory |
| `GET` | `/api/health` | Service health check including Ollama status |

---

## 🧪 Testing Guide

LocalLedger AI comes with a comprehensive test suite of **54 automated unit, integration, and performance tests**.

### Run Backend Pytest Suite
```powershell
cd backend
python -m pytest -v
```

**Test Coverage Highlights**:
- `test_numerical_precision.py`: Formula accuracy, zero-income, zero-expense, boundary amounts ($0.01 to $50M), and 1,500-transaction $O(N)$ performance benchmark (<20ms).
- `test_e2e_integration.py`: Full 12-step API lifecycle flow from upload to analysis, AI Q&A, and privacy purge.
- `test_error_handling.py`: Rejection of corrupted spreadsheets, invalid numbers, empty files, size ceilings, and LLM timeouts.
- `test_privacy_security.py`: Directory traversal sanitization, 10MB limit enforcement, and in-memory deletion.
- `test_ai_analyst.py` & `test_ask_my_business.py`: Fact-checker verification, prompt injection guardrails, and intent classification.

### Verify Production Frontend Build
```powershell
cd frontend
npm run build
```
*Compiles with Next.js Turbopack with 0 TypeScript and 0 lint warnings.*

---

## 🤝 Contributing & Hacktoberfest 2026

Contributions are warmly welcomed! LocalLedger AI is built as part of **Hacktoberfest 2026 (DEV Challenge #1: Open Source)**.

### Good First Issues
- 🌐 Add localized date/currency parsers for additional global banking formats.
- 📉 Add export options (PDF executive report download).
- 🧩 Add support for local ONNX Runtime / `llama.cpp` bindings in addition to Ollama.
- 🎨 Add custom theme presets (e.g. Midnight Blue, Forest, High Contrast).

### Contribution Steps
1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/amazing-feature`).
3. Commit your changes (`git commit -m 'feat: add amazing feature'`).
4. Ensure all tests pass (`python -m pytest -v` in `backend`, `npm run build` in `frontend`).
5. Push to the branch (`git push origin feature/amazing-feature`).
6. Open a Pull Request.

---

## ❓ Frequently Asked Questions (FAQ)

<details>
<summary><strong>Do I need an expensive GPU to run LocalLedger AI?</strong></summary>
<p>
No! Lightweight open-weight models like <code>llama3.2:1b</code> or <code>qwen2.5:1.5b</code> are specifically optimized for everyday laptop and desktop CPUs, requiring less than 1.5 GB of RAM. Furthermore, all deterministic calculations and charts function completely without an AI model running.
</p>
</details>

<details>
<summary><strong>What happens if Ollama is not installed or offline?</strong></summary>
<p>
The application degrades gracefully. All KPI calculations, monthly charts, category distributions, and anomaly flags remain 100% functional. The AI briefing section automatically displays a deterministic mathematical synthesis with zero loss of accuracy.
</p>
</details>

<details>
<summary><strong>Can the AI hallucinate or invent expenses?</strong></summary>
<p>
No. The system uses a strict Anti-Hallucination Grounding Gate. The LLM is given only pre-computed mathematical facts and instructed strictly to cite those exact figures. In addition, an automated validator cross-references every figure in the AI's response against certified metrics.
</p>
</details>

<details>
<summary><strong>Are my bank files saved to my hard drive?</strong></summary>
<p>
No. Uploaded files are parsed directly in server memory and kept in ephemeral session state. They are never written to disk, and clicking "Purge &amp; Reset" instantly removes the ledger from memory.
</p>
</details>

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<p align="center">
  Built with ❤️ for small businesses, privacy advocates, and open-source contributors during <strong>Hacktoberfest 2026</strong>.
</p>
