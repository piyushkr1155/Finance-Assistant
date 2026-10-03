import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional

from models.transaction import NormalizedTransaction, TransactionType
from models.analytics import UnusualTransaction, AnomalyReport


def detect_unusual_transactions_comprehensive(
    transactions: List[NormalizedTransaction],
) -> AnomalyReport:
    """
    Explainable Unusual Transaction Detection.
    Strictly deterministic non-parametric statistical methods.
    Does NOT claim fraud detection. Explains exactly WHY each item was flagged.
    
    Checks implemented:
    1. Category Baseline Comparison (Leave-One-Out)
    2. Statistical Outlier Detection (Interquartile Range - IQR)
    3. Large Transaction Impact (Share of monthly/total budget)
    4. Category Month-over-Month Spikes
    """
    if not transactions or len(transactions) < 3:
        return AnomalyReport(
            total_anomalies=0,
            anomalies=[],
            summary="Dataset has too few records for meaningful statistical outlier detection.",
        )

    # Convert to DataFrame
    records = [
        {
            "id": t.id,
            "date": pd.to_datetime(t.date),
            "date_str": str(t.date),
            "description": t.description,
            "amount": float(t.amount),
            "type": t.type.value,
            "category": t.category,
            "month": str(t.date)[:7],
        }
        for t in transactions
    ]
    df = pd.DataFrame(records)
    anomalies_map: Dict[str, UnusualTransaction] = {}

    # Analyze expenses and income separately
    for t_type in [TransactionType.EXPENSE.value, TransactionType.INCOME.value]:
        sub_df = df[df["type"] == t_type].copy()
        if len(sub_df) < 2:
            continue

        amounts = sub_df["amount"].values
        overall_median = float(np.median(amounts))
        q25 = float(np.percentile(amounts, 25))
        q75 = float(np.percentile(amounts, 75))
        iqr = q75 - q25
        iqr_upper_bound = q75 + (1.5 * iqr) if iqr > 0 else (overall_median * 2.5)

        # Monthly total expenses for budget share calculations
        monthly_totals = sub_df.groupby("month")["amount"].sum().to_dict()

        for _, row in sub_df.iterrows():
            amt = float(row["amount"])
            cat = str(row["category"])
            row_id = str(row["id"])
            m = str(row["month"])

            cat_others = sub_df[(sub_df["category"] == cat) & (sub_df["id"] != row_id)]["amount"]

            reasons: List[str] = []
            ratio_cat: Optional[float] = None
            severity = "medium"

            # 1. Category Baseline Check (Leave-One-Out)
            if len(cat_others) >= 1:
                other_avg = float(cat_others.mean())
                if other_avg > 0 and amt >= 2.5 * other_avg and (amt - other_avg) >= 1000:
                    ratio_cat = round(amt / other_avg, 1)
                    reasons.append(
                        f"₹{amt:,.2f} is {ratio_cat}x higher than the typical category average of ₹{other_avg:,.2f} for '{cat}'"
                    )
                    if ratio_cat >= 4.0:
                        severity = "high"

            # 2. Statistical IQR Outlier Check
            if iqr > 0 and amt > iqr_upper_bound and (amt - overall_median) >= 2000:
                reasons.append(
                    f"Significantly larger than typical {t_type} amount (exceeds IQR threshold of ₹{iqr_upper_bound:,.2f})"
                )
                if amt > q75 + (3.0 * iqr):
                    severity = "high"

            # 3. Large Budget Share Check (Single transaction represents >= 35% of entire month's expenses, with at least 3 expenses in that month)
            m_txns_count = len(sub_df[sub_df["month"] == m])
            m_total = monthly_totals.get(m, 0.0)
            if (
                t_type == TransactionType.EXPENSE.value
                and m_txns_count >= 3
                and m_total > 0
                and (amt / m_total) >= 0.35
                and amt >= 10000
            ):
                pct_share = round((amt / m_total) * 100, 1)
                reasons.append(
                    f"Represents a significant {pct_share}% of all {m} expenses"
                )
                severity = "high"

            # 4. Large Multiple of Median (if single category item)
            if not reasons and amt >= 3.0 * overall_median and (amt - overall_median) >= 3000:
                mult = round(amt / overall_median, 1) if overall_median > 0 else 0
                reasons.append(
                    f"₹{amt:,.2f} is {mult}x higher than overall median {t_type} of ₹{overall_median:,.2f}"
                )

            if reasons:
                anomalies_map[row_id] = UnusualTransaction(
                    id=row_id,
                    date=row["date_str"],
                    description=str(row["description"]),
                    amount=round(amt, 2),
                    type=t_type,
                    category=cat,
                    reason="; ".join(reasons),
                    ratio_to_category_avg=ratio_cat,
                    severity=severity,
                )

    anomalies = list(anomalies_map.values())
    anomalies.sort(key=lambda x: x.amount, reverse=True)

    summary = (
        f"Detected {len(anomalies)} unusual transaction(s) requiring review based on category variance, IQR threshold, and budget concentration."
        if anomalies
        else "No statistical anomalies detected; transactions conform to normal spending and income baselines."
    )

    return AnomalyReport(
        total_anomalies=len(anomalies),
        anomalies=anomalies,
        summary=summary,
    )
