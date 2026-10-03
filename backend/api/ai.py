import json
from fastapi import APIRouter, HTTPException

from services.session_store import session_store
from services.ai_provider import ai_service
from services.context_builder import build_financial_context
from services.prompt_templates import (
    SYSTEM_FINANCIAL_ANALYST_PROMPT,
    build_executive_insights_prompt,
)
from services.ai_validator import validate_ai_response
from services.intent_router import (
    generate_structured_business_answer,
    detect_intent,
)
from services.anomaly_detector import detect_unusual_transactions_comprehensive
from models.ai import (
    AIStatusResponse,
    AIGenerateRequest,
    AIGenerateResponse,
    AskBusinessRequest,
    AskBusinessResponse,
    ExplainAnomalyRequest,
    ExplainAnomalyResponse,
)

router = APIRouter(prefix="/api/ai", tags=["Local AI"])


def generate_deterministic_briefing(context: dict) -> str:
    """Fallback high-precision briefing generated directly from mathematical calculations."""
    kpis = context.get("kpis", {})
    inc = kpis.get("total_income", 0.0)
    exp = kpis.get("total_expenses", 0.0)
    net = kpis.get("net_cash_flow", 0.0)
    margin = kpis.get("savings_rate_pct", 0.0)
    surplus_word = "surplus" if net >= 0 else "deficit"

    top_cats = context.get("top_expense_categories", [])
    cat_summary = ", ".join(
        [f"{c['category']} (₹{c['amount']:,.2f}, {c['percentage']}%)" for c in top_cats[:3]]
    ) or "None recorded"

    latest_perf = context.get("latest_month_performance")
    mom_note = ""
    if latest_perf and latest_perf.get("expense_growth_mom_pct") is not None:
        growth = latest_perf["expense_growth_mom_pct"]
        mom_note = f" In the latest period ({latest_perf['month']}), expenses changed by {growth:+.1f}% compared to the prior month."

    anomalies = context.get("unusual_transactions", [])
    anom_note = ""
    if anomalies:
        top_anom = anomalies[0]
        anom_note = f" Notable variance: {top_anom['description']} (₹{top_anom['amount']:,.2f}) flagged as {top_anom['reason']}."

    return (
        f"Executive Summary ({context.get('period', 'Active Ledger')}):\n\n"
        f"• Financial Health: Total revenue of ₹{inc:,.2f} against expenses of ₹{exp:,.2f}, "
        f"resulting in a net cash {surplus_word} of ₹{net:,.2f} (net margin: {margin:.1f}%).{mom_note}\n\n"
        f"• Primary Expense Drivers: Expenditures are primarily concentrated in {cat_summary}.\n\n"
        f"• Risk & Variance:{anom_note if anom_note else ' All expenses are within normal statistical ranges.'}\n\n"
        f"• Recommended Next Step: Review top category expenditures and verify recurring vendor renewals to maintain positive cash margins."
    )


@router.get("/status", response_model=AIStatusResponse)
def get_ai_status():
    """
    Check if local Ollama daemon is running, inspect installed models,
    and return setup instructions if unavailable.
    """
    return ai_service.get_status()


@router.post("/insights", response_model=AIGenerateResponse)
def get_ai_insights(payload: AIGenerateRequest):
    """
    Generate an executive financial briefing grounded strictly in certified numbers.
    Utilizes local Ollama instance if available, or deterministic synthesis if offline.
    """
    transactions = session_store.get_transactions(payload.session_id)
    if not transactions:
        raise HTTPException(
            status_code=404,
            detail=f"Session '{payload.session_id}' not found. Please upload a file first.",
        )

    # 1. Build deterministic financial context
    context = build_financial_context(payload.session_id)
    context_json = json.dumps(context, indent=2)

    # 2. Check AI status
    ai_status = ai_service.get_status()

    if not ai_status.available or not ai_status.active_model:
        # Graceful fallback: return deterministic executive synthesis
        fallback_briefing = generate_deterministic_briefing(context)
        return AIGenerateResponse(
            success=True,
            model_used="Deterministic Engine (Ollama Standby)",
            response=fallback_briefing,
            is_fallback=True,
            context_used=context,
        )

    # 3. Formulate grounded prompt with strict anti-hallucination guardrails
    user_prompt = build_executive_insights_prompt(context_json)

    # 4. Generate via local Ollama instance
    gen_result = ai_service.generate(
        prompt=user_prompt,
        system=SYSTEM_FINANCIAL_ANALYST_PROMPT,
        model=payload.model or ai_status.active_model,
    )

    if not gen_result.get("success"):
        fallback_briefing = generate_deterministic_briefing(context)
        return AIGenerateResponse(
            success=True,
            model_used=f"{ai_status.active_model} (Fallback)",
            response=fallback_briefing,
            is_fallback=True,
            context_used=context,
        )

    raw_response = gen_result.get("response", "")

    # 5. Output Validation: Verify that numbers match context
    validated_text, is_verified, ungrounded_numbers = validate_ai_response(
        raw_response, context
    )

    return AIGenerateResponse(
        success=True,
        model_used=gen_result.get("model_used"),
        response=validated_text,
        is_fallback=False,
        context_used=context,
    )


@router.post("/ask", response_model=AskBusinessResponse)
def ask_my_business(payload: AskBusinessRequest):
    """
    'Ask My Business' feature.
    Executes intent routing, selects verified analytics, and returns a 4-part structured
    response (ANSWER, KEY DATA, WHY IT MATTERS, WHAT TO CHECK) with certified evidence.
    """
    transactions = session_store.get_transactions(payload.session_id)
    if not transactions:
        raise HTTPException(
            status_code=404,
            detail=f"Session '{payload.session_id}' not found. Please upload a file first.",
        )

    structured_answer = generate_structured_business_answer(
        session_id=payload.session_id,
        query=payload.query,
    )

    return AskBusinessResponse(
        query=payload.query,
        intent=structured_answer["intent"],
        answer=structured_answer["answer"],
        key_data=structured_answer["key_data"],
        why_it_matters=structured_answer["why_it_matters"],
        what_to_check=structured_answer["what_to_check"],
        evidence=structured_answer["evidence"],
    )


@router.post("/explain-anomaly", response_model=ExplainAnomalyResponse)
def explain_anomaly(payload: ExplainAnomalyRequest):
    """
    Generate an explainable AI briefing for a specific flagged unusual transaction.
    Synthesizes why it was flagged and what operational verification is recommended.
    """
    transactions = session_store.get_transactions(payload.session_id)
    if not transactions:
        raise HTTPException(
            status_code=404,
            detail=f"Session '{payload.session_id}' not found. Please upload a file first.",
        )

    report = detect_unusual_transactions_comprehensive(transactions)
    target_anomaly = next((a for a in report.anomalies if a.id == payload.anomaly_id), None)

    if not target_anomaly:
        raise HTTPException(
            status_code=404,
            detail=f"Anomaly with ID '{payload.anomaly_id}' not found.",
        )

    ai_status = ai_service.get_status()
    deterministic_explanation = (
        f"This transaction of ₹{target_anomaly.amount:,.2f} for '{target_anomaly.description}' on {target_anomaly.date} "
        f"stands out because {target_anomaly.reason}."
    )
    recommended_action = (
        f"Verify the vendor contract or invoice for '{target_anomaly.description}' to confirm whether this is a one-time "
        f"capital expenditure or an unexpected rate increase."
    )

    if not ai_status.available or not ai_status.active_model:
        return ExplainAnomalyResponse(
            anomaly_id=target_anomaly.id,
            description=target_anomaly.description,
            amount=target_anomaly.amount,
            category=target_anomaly.category,
            statistical_reason=target_anomaly.reason,
            ai_explanation=deterministic_explanation,
            recommended_action=recommended_action,
            model_used="Deterministic Engine (Ollama Standby)",
            is_fallback=True,
        )

    prompt = (
        f"A business transaction was flagged as an unusual variance:\n"
        f"Date: {target_anomaly.date}\n"
        f"Description: {target_anomaly.description}\n"
        f"Amount: ₹{target_anomaly.amount:,.2f}\n"
        f"Category: {target_anomaly.category}\n"
        f"Statistical Reason: {target_anomaly.reason}\n\n"
        f"Explain in 2 concise sentences why this stands out and what specific question the business owner should ask."
    )

    gen_result = ai_service.generate(
        prompt=prompt,
        system=SYSTEM_FINANCIAL_ANALYST_PROMPT,
        model=ai_status.active_model,
    )

    if gen_result.get("success"):
        return ExplainAnomalyResponse(
            anomaly_id=target_anomaly.id,
            description=target_anomaly.description,
            amount=target_anomaly.amount,
            category=target_anomaly.category,
            statistical_reason=target_anomaly.reason,
            ai_explanation=gen_result.get("response", deterministic_explanation),
            recommended_action=recommended_action,
            model_used=gen_result.get("model_used", ai_status.active_model),
            is_fallback=False,
        )

    return ExplainAnomalyResponse(
        anomaly_id=target_anomaly.id,
        description=target_anomaly.description,
        amount=target_anomaly.amount,
        category=target_anomaly.category,
        statistical_reason=target_anomaly.reason,
        ai_explanation=deterministic_explanation,
        recommended_action=recommended_action,
        model_used=f"{ai_status.active_model} (Fallback)",
        is_fallback=True,
    )
