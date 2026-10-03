# LocalLedger AI

> Understand your business finances with local, privacy-first AI.

[![Hacktoberfest 2026](https://img.shields.io/badge/Hacktoberfest-2026-ff7a00.svg)](https://hacktoberfest.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.13](https://img.shields.io/badge/Python-3.13+-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.141+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-15-black.svg?logo=next.js&logoColor=white)](https://nextjs.org)
[![Ollama](https://img.shields.io/badge/Ollama-Local_AI-white.svg?logo=ollama&logoColor=black)](https://ollama.com)

---

## 📌 Problem
Small business owners generate financial transactions in CSV or Excel format from bank statements, accounting software, and point-of-sale systems. However, small businesses rarely have dedicated financial analysts. Cloud-based AI solutions often pose privacy and data governance concerns when handling confidential ledger and revenue data.

## 💡 Solution
**LocalLedger AI** is an open-source, local-first finance assistant. It ingests standard CSV and Excel transaction files, computes mathematical financial metrics using deterministic Python code, and utilizes an open-weight local LLM via Ollama to provide plain-language explanations, cash flow reviews, and natural language business querying without any data leaving your device.

---

## ⚙️ Architecture at a Glance
```
User
 ↓
Next.js 15 Dashboard (TypeScript + Tailwind CSS + Recharts)
 ↓
FastAPI Backend (Python 3.13 + Pydantic v2)
 ↓
Data Engine (Pandas + openpyxl: File Parsing & Column Normalization)
 ↓
Deterministic Financial Engine (KPIs, Cash Flow, MoM, Outlier Detection)
 ↓
Structured Context Builder (Mathematical Grounding Payload)
 ↓
Local Ollama Instance (llama3.2:1b / qwen2.5:1.5b)
 ↓
Dashboard Presentation & "Ask My Business"
```

---

## 🚀 Quick Start

### Prerequisites
- **Node.js** v20+ / v24+
- **Python** 3.11+ (Tested on Python 3.13)
- **Ollama** (Optional for natural language explanations, core analytics work independently)

### 1. Clone the repository
```bash
git clone https://github.com/your-username/localledger-ai.git
cd localledger-ai
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 3. Frontend Setup
```bash
cd ../frontend
npm install
npm run dev
```

Visit [http://localhost:3000](http://localhost:3000) to access the dashboard.

---

## 🛡️ Privacy & Local AI
- **100% Local Inference:** No transaction amounts, vendor names, or financial summaries are sent to third-party cloud APIs.
- **Deterministic Math:** Financial totals, balances, and growth rates are calculated with deterministic code, never guessed by an LLM.
- **Zero Telemetry:** No tracking, analytics cookies, or external pings.

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).
