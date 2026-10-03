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
from models.ai import (
    AIStatusResponse,
    AIGenerateRequest,
    AIGenerateResponse,
    AskBusinessRequest,
    AskBusinessResponse,
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
        # If model timed out or error occurred, fallback to deterministic briefing
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
