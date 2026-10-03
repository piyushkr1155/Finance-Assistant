import re
from typing import Dict, Any, List, Tuple
from services.context_builder import context_to_numbers_set


def extract_numbers_from_text(text: str) -> List[float]:
    """
    Extracts numerical values from text, stripping currency signs, commas, and percentage signs.
    Ignores common non-financial integers like year 2026 or list numbering (1., 2.).
    """
    cleaned = re.sub(r"\b202[4-9]\b", "", text)  # ignore years like 2026
    cleaned = re.sub(r"^\d+\.\s+", "", cleaned, flags=re.MULTILINE)  # ignore numbered bullets like "1. "

    # Match numbers like ₹1,80,000, $25,000.50, 42.5%, 3500
    pattern = r"[\$₹€£]?\s*([0-9]{1,3}(?:,[0-9]{2,3})*(?:\.[0-9]+)?|[0-9]+(?:\.[0-9]+)?)\s*%?"
    matches = re.findall(pattern, cleaned)

    numbers = []
    for m in matches:
        s = m.replace(",", "").strip()
        try:
            val = float(s)
            # Filter out single digits 0-9 and small integers used for lists or standard words
            if val > 9 or "." in s:
                numbers.append(val)
        except ValueError:
            continue

    return numbers


def validate_ai_response(
    response_text: str,
    context: Dict[str, Any]
) -> Tuple[str, bool, List[float]]:
    """
    Validates that numerical values in the LLM output match the deterministic context.
    Allows a 5% rounding allowance for calculated percentages and sums.
    """
    if not response_text:
        return "", True, []

    context_numbers = context_to_numbers_set(context)
    found_numbers = extract_numbers_from_text(response_text)

    ungrounded = []
    for num in found_numbers:
        # Check if number matches any context number within 5% tolerance
        matches = any(
            abs(num - c_num) <= (max(abs(c_num) * 0.05, 1.0))
            for c_num in context_numbers
        )
        if not matches:
            ungrounded.append(num)

    is_verified = len(ungrounded) == 0

    return response_text, is_verified, ungrounded
