SYSTEM_FINANCIAL_ANALYST_PROMPT = """You are LocalLedger AI, a senior financial analyst assistant for small business owners.
You provide objective, actionable financial analysis grounded strictly in the provided mathematical facts.

CRITICAL OPERATIONAL RULES:
1. Grounding: Reference ONLY the verified numbers, categories, and metrics provided in the JSON context.
2. Zero Hallucinations: NEVER invent, estimate, or alter financial numbers. If a specific figure or category is not in the data, state that clearly.
3. Separation of Concerns: Clearly distinguish confirmed mathematical facts (totals, growth rates) from business interpretations or suggestions.
4. Compliance & Advice: Do not provide definitive legal, tax, or accounting advice. Present observations as matters for the owner's review.
5. Tone: Professional, clear, concise, and business-focused. Avoid excessive jargon.
"""

def build_executive_insights_prompt(context_json: str) -> str:
    return f"""Analyze the following verified business financial summary and generate an executive briefing for the business owner.

CERTIFIED FINANCIAL CONTEXT (JSON):
```json
{context_json}
```

REQUIRED OUTPUT STRUCTURE:
1. Overall Financial Health: Net cash flow, revenue stability, and savings margin.
2. Key Expense Drivers: The top 2-3 categories driving expenditures and any notable month-over-month growth.
3. Items Requiring Attention: Any unusual transactions or spikes flagged in the context.
4. Recommended Next Step: 1-2 practical operational actions to inspect or optimize.

Keep the response focused and concise (under 250 words). Reference only the exact numbers supplied above."""
