# Privacy & Security Architecture

> **Security Philosophy:** LocalLedger AI is built on the foundation of **local-first, data-minimization design**. We do not make misleading claims of "100% security," but rather provide verifiable technical architecture that prevents private financial records from leaving your device.

---

## 1. Zero Cloud Exfiltration (Local AI)
* **Localhost Inference:** Natural-language analysis is handled by an open-weight model running locally via Ollama (`http://127.0.0.1:11434`).
* **Zero Third-Party AI APIs:** No financial numbers, vendor names, or ledger exports are transmitted to cloud AI providers (such as OpenAI, Anthropic, or external inference APIs).
* **Network Isolation:** The core financial analytics engine operates completely offline without requiring an active internet connection once local models are downloaded.

---

## 2. In-Memory Ephemeral Data Lifecycle
* **No Public File Exposure:** Uploaded CSV and XLSX files are parsed directly in RAM into pandas DataFrames. They are **never** stored in public static web roots (such as `frontend/public/` or publicly accessible cloud buckets).
* **On-Demand Memory Purge:** Users can permanently delete their uploaded transaction records and cached analytics at any time via the `DELETE /api/session` endpoint or by clicking "Change File" in the UI.
* **No Database Shadow Copies:** The application does not write shadow transaction logs or unencrypted persistent ledger dumps to disk by default.

---

## 3. Upload Validation & Defense-in-Depth
* **Strict 10MB File Ceiling:** Enforces an absolute file size limit of 10 MB (`MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024`) to protect against memory exhaustion and denial-of-service attempts.
* **Format & MIME Enforcement:** Only `.csv`, `.xlsx`, and `.xls` files are accepted. Unrecognized extensions and malformed binaries are rejected before processing.
* **Filename Sanitization:** All incoming filenames are sanitized using path traversal stripping (`os.path.basename`, removal of `../`, `..\\`), null byte stripping, and character whitelisting to eliminate directory traversal risks.

---

## 4. Anti-Hallucination & Certified Context Isolation
* **No Raw File Dumps to LLMs:** Raw ledger files are never dumped into model context windows.
* **Controlled Mathematical Grounding:** A dedicated Context Builder computes certified totals, category distributions, and statistical variance using deterministic Python code. Only aggregated mathematical facts are presented to the local model.
* **Post-Generation Output Validation:** All numbers generated in AI responses are cross-referenced against the certified context to detect and flag ungrounded statistics.

---

## 5. Logging & Telemetry
* **No Sensitive Financial Logging:** Standard server logs record operational metadata (e.g. execution duration, row counts) and strictly omit vendor names, transaction amounts, and account numbers.
* **Zero Analytics Telemetry:** The application contains zero third-party tracking scripts, advertising trackers, or telemetry beacons.

---

## 6. What This Architecture Does NOT Cover (Realistic Boundaries)
* **Host Machine Security:** If your physical computer or operating system is compromised by malware or unauthorized users, local files and memory can still be accessed.
* **Unencrypted Backups:** If you save manual ledger exports to unencrypted local folders, ensure your local disk encryption (such as BitLocker or FileVault) is active.
