import sys
import os
import json
import time
from fastapi.testclient import TestClient

# Ensure backend modules can be imported
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from main import app
from services.ai_provider import ai_service
from models.ai import AIStatusResponse

client = TestClient(app)

def run_final_demo_verification():
    print("=" * 80)
    print("      LOCALLEDGER AI - PHASE 19 FINAL END-TO-END DEMO TEST SCENARIO      ")
    print("=" * 80)

    # -------------------------------------------------------------
    # Step 1: Health Check & System Status
    # -------------------------------------------------------------
    print("\n[Step 1] System Health & AI Provider Status Check...")
    health_res = client.get("/api/health")
    assert health_res.status_code == 200, f"Health check failed: {health_res.text}"
    health_data = health_res.json()
    print(f" -> Service: {health_data['service']} (Status: {health_data['status']})")
    print(f" -> Ollama Base URL: {health_data['ollama_base_url']}")
    print(f" -> Ollama Available: {health_data.get('ollama_available', False)}")
    print(f" -> Active Model: {health_data.get('active_model', 'None')}")

    # -------------------------------------------------------------
    # Step 2: Ingest 118-Transaction Multi-Month CSV Statement
    # -------------------------------------------------------------
    print("\n[Step 2] Ingesting Multi-Month Ledger Statement (sample_transactions.csv)...")
    csv_file_path = os.path.join(os.path.dirname(__file__), "..", "data", "sample_transactions.csv")
    with open(csv_file_path, "rb") as f:
        file_bytes = f.read()

    upload_res = client.post(
        "/api/upload",
        files={"file": ("sample_transactions.csv", file_bytes, "text/csv")}
    )
    assert upload_res.status_code == 200, f"Upload failed: {upload_res.text}"
    upload_data = upload_res.json()
    session_id = upload_data["session_id"]

    print(f" -> Session ID: {session_id}")
    print(f" -> Detected Columns: {upload_data['columns_detected']}")
    print(f" -> Total Rows Read: {upload_data['total_rows_read']}")
    print(f" -> Valid Transactions: {upload_data['valid_transactions_count']}")
    print(f" -> Corrupted/Invalid Rows: {upload_data['invalid_rows_count']}")
    assert upload_data["valid_transactions_count"] == 118
    assert upload_data["invalid_rows_count"] == 0

    # -------------------------------------------------------------
    # Step 3: Validate Executive KPI Metrics
    # -------------------------------------------------------------
    print("\n[Step 3] Fetching Executive KPI Metrics (/api/analytics/summary)...")
    summary_res = client.get(f"/api/analytics/summary?session_id={session_id}")
    assert summary_res.status_code == 200
    summary = summary_res.json()

    print(f" -> Total Income:       INR {summary['total_income']:,.2f}")
    print(f" -> Total Expenses:     INR {summary['total_expenses']:,.2f}")
    print(f" -> Net Cash Flow:      INR {summary['net_cash_flow']:,.2f}")
    print(f" -> Savings Rate:       {summary['savings_rate_pct']:.1f}%")
    print(f" -> Transaction Count:  {summary['transaction_count']} ({summary['income_transaction_count']} In, {summary['expense_transaction_count']} Out)")
    print(f" -> Date Range:         {summary['start_date']} to {summary['end_date']}")
    print(f" -> Top Income Source:  {summary['top_income_category']}")
    print(f" -> Top Expense Driver: {summary['top_expense_category']}")

    assert summary["total_income"] == 3370700.00
    assert summary["total_expenses"] == 1572800.00
    assert summary["net_cash_flow"] == 1797900.00
    assert summary["savings_rate_pct"] == 53.34
    assert summary["transaction_count"] == 118

    # -------------------------------------------------------------
    # Step 4: Validate Monthly Cash Flow Trends (6 Months)
    # -------------------------------------------------------------
    print("\n[Step 4] Fetching Monthly Trend Series (/api/analytics/monthly)...")
    monthly_res = client.get(f"/api/analytics/monthly?session_id={session_id}")
    assert monthly_res.status_code == 200
    monthly = monthly_res.json()
    assert len(monthly) == 6, f"Expected 6 months, got {len(monthly)}"

    print(f" {'Month':<10} | {'Income':<15} | {'Expenses':<15} | {'Net Cash Flow':<15} | {'Expense MoM':<12}")
    print("-" * 75)
    for m in monthly:
        mom_str = f"{m['expense_growth_pct']:+.1f}%" if m['expense_growth_pct'] is not None else "Baseline"
        print(f" {m['month']:<10} | INR {m['income']:<11,.2f} | INR {m['expenses']:<11,.2f} | INR {m['net']:<11,.2f} | {mom_str:<12}")

    # -------------------------------------------------------------
    # Step 5: Validate Category Allocations (Sum to 100%)
    # -------------------------------------------------------------
    print("\n[Step 5] Fetching Category Breakdown (/api/analytics/categories?type=expense)...")
    cat_res = client.get(f"/api/analytics/categories?session_id={session_id}&type=expense")
    assert cat_res.status_code == 200
    categories = cat_res.json()
    total_pct = sum(c["percentage"] for c in categories)
    print(f" -> Total Categories: {len(categories)}")
    for c in categories:
        print(f"    • {c['category']:<25}: INR {c['amount']:>10,.2f} ({c['percentage']:>5.1f}%, {c['transaction_count']} txns)")
    print(f" -> Cumulative Percentage Sum: {total_pct:.2f}% (Verified == 100%)")
    assert 99.8 <= total_pct <= 100.2

    # -------------------------------------------------------------
    # Step 6: Validate Largest Expenses
    # -------------------------------------------------------------
    print("\n[Step 6] Fetching Top 5 Largest Expenditures (/api/analytics/largest?type=expense)...")
    largest_res = client.get(f"/api/analytics/largest?session_id={session_id}&type=expense&limit=5")
    assert largest_res.status_code == 200
    largest = largest_res.json()
    for idx, t in enumerate(largest, 1):
        print(f"    {idx}. [{t['date']}] {t['description']:<50} : INR {t['amount']:>10,.2f} ({t['category']})")
    assert largest[0]["amount"] == 148000.0  # Apple Workstation
    assert largest[1]["amount"] == 98000.0   # Monthly Team Payroll
    assert largest[2]["amount"] == 98000.0   # Monthly Team Payroll
    assert largest[3]["amount"] == 98000.0   # Monthly Team Payroll
    assert largest[4]["amount"] == 94500.0   # AWS 1-Year Prepayment

    # -------------------------------------------------------------
    # Step 7: Validate Statistical Outliers & 4 Real-World Anomalies
    # -------------------------------------------------------------
    print("\n[Step 7] Detecting Statistical Outliers (/api/analytics/anomalies)...")
    anom_res = client.get(f"/api/analytics/anomalies?session_id={session_id}")
    assert anom_res.status_code == 200
    anom_data = anom_res.json()
    anomalies = anom_data["anomalies"]
    print(f" -> Total Anomalies Flagged: {anom_data['total_anomalies']}")

    # Check for the 4 intentional anomalies
    descriptions = [a["description"] for a in anomalies]
    has_aws_prepayment = any("AWS 1-Year" in d for d in descriptions)
    has_mac_workstation = any("Apple Workstation" in d for d in descriptions)
    has_ad_blitz = any("Product Launch" in d for d in descriptions)
    has_ip_trademark = any("Corporate IP Trademark" in d for d in descriptions)

    print(f"    [x] Anomaly 1 (July AWS Reserved Prepayment INR 94.5k):     {has_aws_prepayment}")
    print(f"    [x] Anomaly 2 (August Apple Mac Studio Workstation INR 148k): {has_mac_workstation}")
    print(f"    [x] Anomaly 3 (September Product Launch Ad Blitz INR 72k):    {has_ad_blitz}")
    print(f"    [x] Anomaly 4 (October Corporate IP Legal Retainer INR 58k):  {has_ip_trademark}")
    assert has_aws_prepayment and has_mac_workstation and has_ad_blitz and has_ip_trademark

    # -------------------------------------------------------------
    # Step 8: Executive AI Financial Briefing
    # -------------------------------------------------------------
    print("\n[Step 8] Generating Executive Financial Briefing (/api/ai/insights)...")
    insights_res = client.post("/api/ai/insights", json={"session_id": session_id})
    assert insights_res.status_code == 200
    insights = insights_res.json()
    print(f" -> Model Used: {insights['model_used']}")
    print(f" -> Fallback State: {insights['is_fallback']}")
    print(f" -> Certified Briefing Preview:\n")
    print(insights["response"][:350] + "...\n")
    assert len(insights["response"]) > 100

    # -------------------------------------------------------------
    # Step 9: "Ask My Business" Grounded Natural Language Q&A
    # -------------------------------------------------------------
    print("\n[Step 9] Testing 'Ask My Business' Grounded Q&A (/api/ai/ask)...")
    test_queries = [
        "Why did my expenses increase in September?",
        "What are my biggest expense categories?",
        "What is my net cash flow and operating margin?",
    ]

    for q in test_queries:
        ask_res = client.post("/api/ai/ask", json={"session_id": session_id, "query": q})
        assert ask_res.status_code == 200
        ask_data = ask_res.json()
        print(f" -> Query: '{q}'")
        print(f"    Intent: {ask_data['intent']}")
        print(f"    Answer: {ask_data['answer'][:120]}...")
        print(f"    Key Data: {ask_data['key_data']}")
        print(f"    Why It Matters: {ask_data['why_it_matters'][:80]}...")
        print()

    # -------------------------------------------------------------
    # Step 10: Explain Flagged Anomaly with AI
    # -------------------------------------------------------------
    target_anom = next(a for a in anomalies if "Apple Workstation" in a["description"])
    print(f"\n[Step 10] Explaining Specific Anomaly with AI (/api/ai/explain-anomaly)...")
    print(f" -> Target: {target_anom['description']} (INR {target_anom['amount']:,.2f})")
    explain_res = client.post(
        "/api/ai/explain-anomaly",
        json={"session_id": session_id, "anomaly_id": target_anom["id"]}
    )
    assert explain_res.status_code == 200
    exp_data = explain_res.json()
    print(f" -> Statistical Reason: {exp_data['statistical_reason']}")
    print(f" -> AI Explanation:     {exp_data['ai_explanation']}")
    print(f" -> Recommended Step:   {exp_data['recommended_action']}")
    assert len(exp_data["ai_explanation"]) > 0

    # -------------------------------------------------------------
    # Step 11: Ephemeral Privacy Purge
    # -------------------------------------------------------------
    print(f"\n[Step 11] Purging Ephemeral Session from Memory (DELETE /api/session)...")
    purge_res = client.delete(f"/api/session?session_id={session_id}")
    assert purge_res.status_code == 200
    assert purge_res.json()["status"] == "purged"
    print(f" -> Successfully purged session {session_id}")

    # Subsequent access MUST return 404
    post_purge_summary = client.get(f"/api/analytics/summary?session_id={session_id}")
    assert post_purge_summary.status_code == 404
    print(f" -> Verified HTTP 404 on purged session access (Zero lingering memory).")

    # -------------------------------------------------------------
    # Step 12: Ingest Excel Workbook Statement (sample_transactions.xlsx)
    # -------------------------------------------------------------
    print("\n[Step 12] Ingesting Binary Excel Workbook (sample_transactions.xlsx)...")
    xlsx_file_path = os.path.join(os.path.dirname(__file__), "..", "data", "sample_transactions.xlsx")
    with open(xlsx_file_path, "rb") as f:
        xlsx_bytes = f.read()

    upload_xlsx = client.post(
        "/api/upload",
        files={"file": ("sample_transactions.xlsx", xlsx_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    )
    assert upload_xlsx.status_code == 200
    xlsx_data = upload_xlsx.json()
    print(f" -> Excel Workbook Ingested: {xlsx_data['valid_transactions_count']} valid rows, format={xlsx_data['file_type']}")
    assert xlsx_data["valid_transactions_count"] == 118
    assert xlsx_data["file_type"] == "XLSX"

    # Purge second session
    client.delete(f"/api/session?session_id={xlsx_data['session_id']}")

    print("\n" + "=" * 80)
    print("      ALL 12 END-TO-END DEMO TEST SCENARIOS PASSED WITH 100% SUCCESS      ")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    run_final_demo_verification()
