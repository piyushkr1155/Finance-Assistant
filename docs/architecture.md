# LocalLedger AI — System Architecture & Data Flow

> Technical specification, architectural diagrams, and trust boundaries for LocalLedger AI (Hacktoberfest 2026 DEV Challenge #1).

---

## 1. Core Architectural Principles

LocalLedger AI was engineered from the ground up to solve the fundamental conflict between financial confidentiality and modern artificial intelligence. It adheres to four non-negotiable principles:

1. **Strict Separation of Arithmetic and Language**:
   - **Math is Deterministic**: Large Language Models are never permitted to calculate sums, growth percentages, category totals, or outlier thresholds. All calculations are executed in Python using vectorized NumPy/Pandas algorithms.
   - **Language is Grounded**: The local LLM acts exclusively as an executive translator, converting certified numerical facts into plain-English narratives and actionable advice.
2. **100% On-Device Confidentiality**:
   - No ledger rows, customer identifiers, or financial metrics leave the host machine. All AI inference communicates over `http://127.0.0.1:11434` with the local Ollama daemon.
3. **Ephemeral In-Memory Lifecycle**:
   - Ledgers and calculated metrics live solely in server RAM. No persistent disk writes, no unencrypted SQLite/PostgreSQL tables, and zero long-term shadow copies.
4. **Graceful Fault Tolerance**:
   - If local AI is offline, all analytical dashboards, charts, and anomaly detectors remain 100% operational with deterministic executive synthesis fallbacks.

---

## 2. High-Level System Architecture

The following diagram illustrates the complete end-to-end system topology:

```mermaid
graph TD
    subgraph Client_Browser ["User Workspace (Browser)"]
        UI["Next.js 16 Dashboard (Turbopack)"]
        Upload["File Dropzone & Demo Loader"]
        Charts["Recharts Visualizations (Bar & Donut)"]
        QA["Ask My Business (4-Part Q&A)"]
        AnomUI["Unusual Transactions with AI Drawers"]
    end

    subgraph Host_Machine_Backend ["Local Backend (FastAPI - Port 8000)"]
        Router["FastAPI REST Routers (/api/*)"]
        Parser["File Parser & Path Sanitizer"]
        Normalizer["Column Heuristics & Data Normalizer"]
        SessionRAM[("Ephemeral Session Store (RAM Only)")]
        Analytics["Deterministic Analytics Engine"]
        AnomalyDet["O(N) Statistical Anomaly Detector"]
        ContextBld["Structured Context Builder"]
        IntentRouter["Financial Intent Classifier"]
        Validator["Fact-Checking Numerical Validator"]
    end

    subgraph Local_AI_Engine ["Local AI Subsystem (Ollama - Port 11434)"]
        OllamaDaemon["Ollama Daemon (127.0.0.1:11434)"]
        OpenWeightModel["Llama 3.2 1B / Qwen 2.5 1.5B (Local Weights)"]
    end

    subgraph External_Cloud ["External World (Untrusted Cloud)"]
        CloudBlocked["BLOCKED / ZERO OUTBOUND TRAFFIC"]
    end

    %% Connections
    Upload -->|"1. Uploads CSV/XLSX"| Router
    Router --> Parser
    Parser --> Normalizer
    Normalizer -->|"2. Stores Normalized Txns"| SessionRAM

    SessionRAM --> Analytics
    SessionRAM --> AnomalyDet

    Analytics -->|"3. KPIs, Trends, Categories"| Charts
    AnomalyDet -->|"4. Flagged Outliers"| AnomUI

    Analytics --> ContextBld
    AnomalyDet --> ContextBld
    ContextBld -->|"5. Certified Math Context"| Router

    QA -->|"6. Natural Language Query"| IntentRouter
    IntentRouter --> ContextBld
    ContextBld -->|"7. Grounded Prompt"| OllamaDaemon
    OllamaDaemon --> OpenWeightModel
    OpenWeightModel -->|"8. Raw Response"| Validator
    Validator -->|"9. Validated Narrative"| UI

    %% Privacy Boundary
    Host_Machine_Backend -.->|"NO NETWORK EGRESS"| CloudBlocked

    style External_Cloud fill:#ffebee,stroke:#c62828,stroke-width:2px;
    style Local_AI_Engine fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px;
    style Host_Machine_Backend fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
    style Client_Browser fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px;
```

---

## 3. The 100% On-Device Trust Boundary

LocalLedger AI enforces a strict containment perimeter. All sensitive financial data is enclosed strictly within the user's local operating system:

```mermaid
flowchart LR
    subgraph UserDevice ["PHYSICAL USER DEVICE / WORKSTATION"]
        direction TB
        subgraph FrontendScope ["Browser Sandbox"]
            NextApp["Next.js Single Page App\n(localhost:3000)"]
        end

        subgraph BackendScope ["Application Memory"]
            FastAPIServer["FastAPI Server\n(127.0.0.1:8000)"]
            RAMStorage[("In-Memory Session Store\n(Volatile RAM)")]
            MathRoutines["Deterministic Python Core\n(NumPy / Pandas)"]
        end

        subgraph AIScope ["Local AI Sandbox"]
            OllamaInstance["Ollama Daemon\n(127.0.0.1:11434)"]
            LocalLLM["Local Model Weights\n(e.g., Llama 3.2 1B)"]
        end
    end

    subgraph PublicInternet ["PUBLIC INTERNET / EXTERNAL CLOUD"]
        CloudAI["Third-Party AI APIs\n(OpenAI, Anthropic, Google)"]
        DataBrokers["Analytics & Tracking Brokers"]
    end

    %% Internal flow
    NextApp <===>|"HTTP / JSON\n(localhost only)"| FastAPIServer
    FastAPIServer <===> MathRoutines
    FastAPIServer <===> RAMStorage
    FastAPIServer <===>|"Local REST API\n(127.0.0.1 only)"| OllamaInstance
    OllamaInstance <===> LocalLLM

    %% Blocked flow
    FastAPIServer -.->|"X BLOCKED (No Egress)"| CloudAI
    NextApp -.->|"X BLOCKED (No Telemetry)"| DataBrokers

    style PublicInternet fill:#ffebee,stroke:#d32f2f,stroke-width:2px,stroke-dasharray: 5 5;
    style UserDevice fill:#f1f8e9,stroke:#388e3c,stroke-width:3px;
```

---

## 4. Ingestion & Normalization Pipeline

Handling arbitrary small business statements requires handling diverse date formats, signed amounts, separate debit/credit columns, and variable encoding standards:

```mermaid
sequenceDiagram
    autonumber
    actor User as Business Owner
    participant Web as Next.js 16 Dropzone
    participant Parser as File Parser
    participant Norm as Normalizer
    participant Store as Session Store (RAM)

    User->>Web: Drops statement (CSV or XLSX, <= 10MB)
    Web->>Parser: POST /api/upload (Multipart stream)
    
    Note over Parser: 1. Sanitize Filename (strip ../, null-bytes)<br/>2. Size Check (<= 10,485,760 bytes)<br/>3. Format Check (.csv, .xlsx, .xls)
    
    alt CSV File
        Parser->>Parser: Try Encodings (UTF-8, Latin-1, CP1252)<br/>Try Delimiters (Comma, Semicolon, Tab)
    else Excel File
        Parser->>Parser: OpenPyXL stream reading<br/>Catch corrupted ZIP/header errors
    end

    Parser->>Norm: Raw DataFrame & Detected Columns
    Note over Norm: Heuristic Synonym Matcher:<br/>• Date: date, txn_date, booking_date<br/>• Amount: amount, net, total<br/>• Debit/Credit: debit, credit, withdrawal, deposit<br/>• Category: category, expense_type, group

    Norm->>Norm: Parse Flexible Dates & Sanitize Currency Symbols ($, INR, Rs, €, £)
    Norm->>Norm: Drop completely invalid rows -> InvalidRowDetail[]
    Norm->>Store: Store DataFrame, Mapping, & Normalized Transactions
    Store-->>Web: Return Session ID, Column Mappings, Counts & Sample Preview
```

---

## 5. Statistical Anomaly Detection Pipeline

Rather than relying on vague prompts to spot anomalies, LocalLedger AI uses a multi-faceted statistical filter executing in $O(N)$ time:

```mermaid
flowchart TD
    Start["Normalized Transactions List"] --> Split["Split by Type: Expenses vs Income"]
    
    subgraph Precompute ["O(N) Vectorized Aggregations"]
        Agg1["Monthly Totals & Counts via GroupBy"]
        Agg2["Category Sums & Counts via GroupBy"]
        Agg3["Compute Median, Q1, Q3, & IQR = Q3 - Q1"]
    end
    Split --> Precompute

    Precompute --> Loop["Iterate Transactions in O(1) per row"]

    subgraph Checks ["Triple-Filter Evaluation"]
        Check1{"1. Category Baseline:<br/>Amt >= 2.5x Leave-One-Out Mean<br/>and Delta >= ₹1,000?"}
        Check2{"2. Non-Parametric IQR:<br/>Amt > Q3 + 1.5*IQR<br/>and Delta >= ₹2,000?"}
        Check3{"3. Monthly Concentration:<br/>Single Txn >= 35% of Monthly Budget<br/>(and >= 3 txns in month)?"}
    end

    Loop --> Check1
    Check1 -->|Yes| Flag1["Tag: Category Variance Spike"]
    Check1 -->|No| Check2
    Check2 -->|Yes| Flag2["Tag: Statistical IQR Outlier"]
    Check2 -->|No| Check3
    Check3 -->|Yes| Flag3["Tag: Heavy Budget Share"]
    Check3 -->|No| Safe["Conforms to Baseline"]

    Flag1 --> Assemble["Aggregate Anomalies & Sort Descending by Value"]
    Flag2 --> Assemble
    Flag3 --> Assemble

    Assemble --> Report["AnomalyReport Payload with Severity (HIGH / MEDIUM)"]
```

---

## 6. Two-Tier Grounded AI Reasoning & Validation

When the user requests an executive summary or asks a business question, the local AI is bound by an anti-hallucination contract:

```mermaid
sequenceDiagram
    autonumber
    actor User as Business Owner
    participant UI as Next.js Dashboard
    participant API as FastAPI Backend
    participant CB as Context Builder
    participant Ollama as Local Ollama Daemon
    participant Val as AI Fact Validator

    User->>UI: Clicks "Generate Executive Briefing"
    UI->>API: POST /api/ai/insights { session_id }

    API->>CB: build_financial_context(session_id)
    Note over CB: 1. Extract exact Summary KPIs<br/>2. Extract Monthly Trend series & MoM rates<br/>3. Extract Top Category amounts & percentages<br/>4. Extract Top Anomalies & reasons<br/>Output: Pure JSON Context Payload

    alt Ollama Offline / Standby
        API-->>UI: Return Deterministic Briefing (Zero Degradation)
    else Ollama Online
        API->>Ollama: POST /api/generate<br/>System Prompt: Strict Financial Analyst Guardrails<br/>User Prompt: Grounded Narrative Request + Certified JSON
        Note over Ollama: Local Inference (temperature=0.1)<br/>Model: llama3.2:1b or qwen2.5:1.5b
        Ollama-->>API: Raw LLM Output Text
        API->>Val: validate_ai_response(response, context)
        Note over Val: Cross-reference extracted numbers<br/>against certified numerical context<br/>(5% rounding tolerance)
        Val-->>API: Verified Briefing + Discrepancy Warnings
        API-->>UI: Return AIGenerateResponse (Narrative, Model, Context)
        UI->>User: Displays Formatted Briefing with Copy Button
    end
```

---

## 7. "Ask My Business" Intent Routing State Machine

Natural language questions are parsed through a multi-class financial intent router:

```mermaid
stateDiagram-v2
    [*] --> IngestQuery: User enters natural language prompt

    IngestQuery --> DetectIntent: Match keywords, regex & semantic patterns
    
    DetectIntent --> ExpenseIncrease: "Why did expenses increase?" / "spike"
    DetectIntent --> UnusualTxns: "What looks unusual?" / "weird" / "outlier"
    DetectIntent --> CategoryBreakdown: "Biggest categories" / "where does money go"
    DetectIntent --> CashFlowProfit: "Cash flow" / "profit" / "savings rate" / "margin"
    DetectIntent --> GeneralInquiry: All other inquiries

    ExpenseIncrease --> BuildStructured: Extract latest MoM surge & top category drivers
    UnusualTxns --> BuildStructured: Extract top flagged statistical anomalies
    CategoryBreakdown --> BuildStructured: Extract ranked category distribution
    CashFlowProfit --> BuildStructured: Extract net revenue, surplus/deficit & margin
    GeneralInquiry --> BuildStructured: Fallback to high-level financial summary

    BuildStructured --> Render4Part: Format 4-Part Response:
    note right of Render4Part
      1. Direct Grounded Answer
      2. Certified Numerical Data Points
      3. Why It Matters
      4. Recommended Action Items
    end note

    Render4Part --> [*]: Return AskBusinessResponse to Dashboard
```

---

## 8. Ephemeral Session Lifecycle & Memory Purge

Financial data exists in RAM only for the active working session:

```mermaid
sequenceDiagram
    autonumber
    actor User as Business Owner
    participant UI as Dashboard UI
    participant Backend as FastAPI Memory
    participant RAM as Session RAM Map

    User->>UI: Uploads file
    UI->>Backend: POST /api/upload
    Backend->>RAM: session_store.set(session_id, data)
    RAM-->>Backend: OK
    Backend-->>UI: session_id = "a1b2c3d4..."

    Note over User,RAM: User explores KPIs, charts, and queries local AI

    User->>UI: Clicks "Purge & Reset"
    UI->>Backend: DELETE /api/session?session_id=a1b2c3d4...
    Backend->>RAM: session_store.delete(session_id)
    Note over RAM: del self._sessions[session_id]<br/>Python GC reclaims memory
    RAM-->>Backend: Purged
    Backend-->>UI: 200 OK { status: "purged" }

    Note over UI: Subsequent queries for old session_id return 404 Not Found
    UI->>Backend: GET /api/analytics/summary?session_id=a1b2c3d4...
    Backend-->>UI: 404 Not Found (Session erased)
```

---

## 9. Performance & Complexity Analysis

| Operation | Algorithm / Mechanism | Time Complexity | Real-World Benchmark (1,500 Txns) |
| :--- | :--- | :--- | :--- |
| **File Parsing** | OpenPyXL / Pandas `read_csv` | $O(N)$ | ~12ms |
| **Column Normalization** | Vectorized clean regex & datetime parse | $O(N)$ | ~18ms |
| **KPI Aggregations** | Vectorized NumPy sum, diff, divide | $O(1)$ post-aggregation | < 2ms |
| **Monthly Trends & MoM** | Pandas `groupby("month")` | $O(N \log M)$ | ~4ms |
| **Category Breakdown** | Pandas `groupby("category")` | $O(N \log C)$ | ~3ms |
| **Statistical Outlier Scan**| Precomputed group aggregations + Leave-One-Out | $O(N)$ | ~15ms |
| **Local AI Inference** | 4-bit Quantized Llama 3.2 1B via Ollama | Depends on token length | ~400ms – 1,200ms on CPU |
