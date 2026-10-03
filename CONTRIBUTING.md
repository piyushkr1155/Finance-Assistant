# Contributing to LocalLedger AI

Thank you for your interest in contributing to **LocalLedger AI**! We are participating in **Hacktoberfest 2026 (DEV Challenge #1: Open Source)**. We welcome contributions from developers, accountants, designers, and documentation writers of all skill levels.

---

## 🎯 Architectural Ground Rules

Before submitting code, please understand our core engineering principles:

1. **Deterministic Calculations Only**: All arithmetic (totals, margins, percentages, growth rates, outlier bounds) must be computed in Python using deterministic mathematical algorithms. **Never use an LLM to calculate numbers.**
2. **100% On-Device Privacy**: No code may introduce external cloud AI APIs, remote telemetry scripts, third-party analytics pixels, or unauthorized network calls. All AI reasoning must route through local open-weight models (via Ollama or local runtimes).
3. **In-Memory Storage**: Do not introduce unencrypted database writes or write ledger files to public web directories. Data exists only in volatile server RAM.
4. **Tested Changes**: All new analytics or backend features must include automated Pytest unit tests in `backend/tests/`. All frontend code must pass `npm run build` with zero TypeScript errors.

---

## 🚀 Development Setup

### 1. Fork & Clone
```bash
# Fork the repo on GitHub, then clone your fork:
git clone https://github.com/<your-username>/Finance-Assistant.git
cd Finance-Assistant
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv

# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

### 3. Frontend Setup
```bash
cd ../frontend
npm install
npm run dev
```

### 4. Running Tests
```bash
# Backend tests
cd backend
python -m pytest -v

# Frontend build check
cd ../frontend
npm run build
```

---

## 💡 Good First Issues

Looking for inspiration? Here are great ways to contribute:
- **Banking Formats**: Add support for specialized regional CSV exports (e.g. HDFC, SBI, Chase, Barclays, Revolut).
- **Export Formats**: Add a 1-click "Download PDF Financial Summary" button.
- **Visual Themes**: Add custom color schemes (e.g., Midnight Blue, Warm Sepia, High-Contrast Accessibility).
- **Alternative Local Runtimes**: Add an ONNX Runtime or `llama.cpp` provider alongside the existing Ollama provider in `backend/services/ai_provider.py`.
- **Localization**: Translate the UI and executive briefing templates into additional languages.

---

## 📝 Pull Request Checklist

When submitting a Pull Request, please ensure:
- [ ] Code follows conventional commit style: `feat: ...`, `fix: ...`, `docs: ...`, `test: ...`.
- [ ] All 54+ backend unit and integration tests pass (`python -m pytest -v`).
- [ ] Frontend compiles with zero TypeScript errors (`npm run build`).
- [ ] No private API keys, secrets, or hardcoded personal credentials are included.
- [ ] Documentation is updated if you added a new API endpoint or configuration variable.

---

## 📜 Code of Conduct

All contributors are expected to uphold our [Code of Conduct](CODE_OF_CONDUCT.md) to ensure a welcoming, inclusive, and harassment-free community.
