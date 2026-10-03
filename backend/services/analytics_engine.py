import numpy as np
import pandas as pd
from typing import List, Optional, Dict, Any

from models.transaction import NormalizedTransaction, TransactionType
from models.analytics import (
    SummaryKPIs,
    MonthlyMetric,
    CategoryBreakdown,
    LargestTransaction,
    UnusualTransaction,
    AnomalyReport,
)


def transactions_to_df(transactions: List[NormalizedTransaction]) -> pd.DataFrame:
    """Converts a list of NormalizedTransaction models into a typed pandas DataFrame."""
    if not transactions:
        return pd.DataFrame(
            columns=["id", "date", "description", "amount", "type", "category"]
        )

    records = [
        {
            "id": t.id,
            "date": pd.to_datetime(t.date),
            "description": t.description,
            "amount": float(t.amount),
            "type": t.type.value,
            "category": t.category,
        }
        for t in transactions
    ]
    df = pd.DataFrame(records)
    return df


def calculate_summary(transactions: List[NormalizedTransaction]) -> SummaryKPIs:
    """
    Computes deterministic overall financial summary and KPIs.
    """
    if not transactions:
        return SummaryKPIs(
            total_income=0.0,
            total_expenses=0.0,
            net_cash_flow=0.0,
            savings_rate_pct=0.0,
            transaction_count=0,
            income_transaction_count=0,
            expense_transaction_count=0,
            avg_transaction_amount=0.0,
            avg_income=0.0,
            avg_expense=0.0,
            start_date=None,
            end_date=None,
            top_expense_category=None,
            top_income_category=None,
        )

    df = transactions_to_df(transactions)

    income_df = df[df["type"] == TransactionType.INCOME.value]
    expense_df = df[df["type"] == TransactionType.EXPENSE.value]

    total_income = float(income_df["amount"].sum())
    total_expenses = float(expense_df["amount"].sum())
    net_cash_flow = total_income - total_expenses

    savings_rate = (
        round((net_cash_flow / total_income) * 100, 2) if total_income > 0 else 0.0
    )

    avg_txn = float(df["amount"].mean())
    avg_inc = float(income_df["amount"].mean()) if not income_df.empty else 0.0
    avg_exp = float(expense_df["amount"].mean()) if not expense_df.empty else 0.0

    min_date = str(df["date"].min().date())
    max_date = str(df["date"].max().date())

    top_exp_cat = None
    if not expense_df.empty:
        top_exp_cat = str(expense_df.groupby("category")["amount"].sum().idxmax())

    top_inc_cat = None
    if not income_df.empty:
        top_inc_cat = str(income_df.groupby("category")["amount"].sum().idxmax())

    return SummaryKPIs(
        total_income=round(total_income, 2),
        total_expenses=round(total_expenses, 2),
        net_cash_flow=round(net_cash_flow, 2),
        savings_rate_pct=savings_rate,
        transaction_count=len(df),
        income_transaction_count=len(income_df),
        expense_transaction_count=len(expense_df),
        avg_transaction_amount=round(avg_txn, 2),
        avg_income=round(avg_inc, 2),
        avg_expense=round(avg_exp, 2),
        start_date=min_date,
        end_date=max_date,
        top_expense_category=top_exp_cat,
        top_income_category=top_inc_cat,
    )


def calculate_monthly_trends(transactions: List[NormalizedTransaction]) -> List[MonthlyMetric]:
    """
    Computes deterministic monthly breakdown, net cash flow, and month-over-month growth rates.
    """
    if not transactions:
        return []

    df = transactions_to_df(transactions)
    df["month"] = df["date"].dt.strftime("%Y-%m")

    # Aggregate by month and type
    monthly_groups = df.groupby(["month", "type"])["amount"].sum().unstack(fill_value=0.0)

    if TransactionType.INCOME.value not in monthly_groups.columns:
        monthly_groups[TransactionType.INCOME.value] = 0.0
    if TransactionType.EXPENSE.value not in monthly_groups.columns:
        monthly_groups[TransactionType.EXPENSE.value] = 0.0

    counts_by_month = df.groupby("month")["id"].count()

    metrics: List[MonthlyMetric] = []
    prev_income = None
    prev_expense = None

    for month_str in sorted(monthly_groups.index):
        inc = float(monthly_groups.loc[month_str, TransactionType.INCOME.value])
        exp = float(monthly_groups.loc[month_str, TransactionType.EXPENSE.value])
        net = inc - exp
        count = int(counts_by_month.get(month_str, 0))

        # MoM growth calculations
        inc_growth = None
        if prev_income is not None:
            if prev_income > 0:
                inc_growth = round(((inc - prev_income) / prev_income) * 100, 2)
            elif inc > 0:
                inc_growth = 100.0
            else:
                inc_growth = 0.0

        exp_growth = None
        if prev_expense is not None:
            if prev_expense > 0:
                exp_growth = round(((exp - prev_expense) / prev_expense) * 100, 2)
            elif exp > 0:
                exp_growth = 100.0
            else:
                exp_growth = 0.0

        metrics.append(
            MonthlyMetric(
                month=month_str,
                income=round(inc, 2),
                expenses=round(exp, 2),
                net=round(net, 2),
                transaction_count=count,
                income_growth_pct=inc_growth,
                expense_growth_pct=exp_growth,
            )
        )

        prev_income = inc
        prev_expense = exp

    return metrics


def calculate_category_breakdown(
    transactions: List[NormalizedTransaction],
    txn_type: str = "expense",
) -> List[CategoryBreakdown]:
    """
    Computes spending or income breakdown grouped by category with percentages and counts.
    """
    if not transactions:
        return []

    df = transactions_to_df(transactions)
    filtered = df[df["type"].str.lower() == txn_type.lower()]

    if filtered.empty:
        return []

    total_amount = filtered["amount"].sum()
    grouped = (
        filtered.groupby("category")
        .agg(
            amount=("amount", "sum"),
            count=("id", "count"),
            avg=("amount", "mean"),
        )
        .reset_index()
    )

    # Sort descending by total amount
    grouped = grouped.sort_values(by="amount", ascending=False)

    results: List[CategoryBreakdown] = []
    for _, row in grouped.iterrows():
        pct = round((row["amount"] / total_amount) * 100, 2) if total_amount > 0 else 0.0
        results.append(
            CategoryBreakdown(
                category=str(row["category"]),
                amount=round(float(row["amount"]), 2),
                percentage=pct,
                transaction_count=int(row["count"]),
                avg_per_transaction=round(float(row["avg"]), 2),
            )
        )

    return results


def get_largest_transactions(
    transactions: List[NormalizedTransaction],
    txn_type: Optional[str] = None,
    limit: int = 10,
) -> List[LargestTransaction]:
    """
    Retrieves the largest transactions by value.
    """
    if not transactions:
        return []

    df = transactions_to_df(transactions)
    if txn_type:
        df = df[df["type"].str.lower() == txn_type.lower()]

    if df.empty:
        return []

    top_df = df.sort_values(by="amount", ascending=False).head(limit)

    results: List[LargestTransaction] = []
    for _, row in top_df.iterrows():
        results.append(
            LargestTransaction(
                id=str(row["id"]),
                date=row["date"].strftime("%Y-%m-%d"),
                description=str(row["description"]),
                amount=round(float(row["amount"]), 2),
                type=str(row["type"]),
                category=str(row["category"]),
            )
        )

    return results


def detect_unusual_transactions(
    transactions: List[NormalizedTransaction],
) -> AnomalyReport:
    """
    Deterministic Unusual Transaction Detection.
    Uses robust non-parametric statistics (IQR and Leave-One-Out Category Baselines)
    so extreme values do not artificially mask themselves by skewing the baseline.
    Never claims fraud; clearly explains statistical basis.
    """
    if not transactions or len(transactions) < 3:
        return AnomalyReport(
            total_anomalies=0,
            anomalies=[],
            summary="Dataset has too few records for meaningful statistical outlier detection.",
        )

    df = transactions_to_df(transactions)
    anomalies: List[UnusualTransaction] = []

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

        for _, row in sub_df.iterrows():
            amt = float(row["amount"])
            cat = str(row["category"])
            row_id = str(row["id"])

            # Category items excluding this current transaction (Leave-One-Out)
            cat_others = sub_df[(sub_df["category"] == cat) & (sub_df["id"] != row_id)]["amount"]

            reasons = []
            ratio_cat = None
            severity = "medium"

            # Check 1: Category Baseline Comparison (Leave-One-Out)
            if len(cat_others) >= 1:
                other_avg = float(cat_others.mean())
                if other_avg > 0 and amt >= 2.5 * other_avg and (amt - other_avg) >= 1000:
                    ratio_cat = round(amt / other_avg, 1)
                    reasons.append(
                        f"{ratio_cat}x higher than the typical category average of ₹{other_avg:,.2f} for '{cat}'"
                    )
                    if ratio_cat >= 4.0:
                        severity = "high"

            # Check 2: Statistical IQR Outlier across this transaction type
            if iqr > 0 and amt > iqr_upper_bound and (amt - overall_median) >= 2000:
                reasons.append(
                    f"Significantly exceeds typical {t_type} range (upper IQR threshold: ₹{iqr_upper_bound:,.2f})"
                )
                if amt > q75 + (3.0 * iqr):
                    severity = "high"

            # Check 3: Large Multiple of Median if category baseline is unavailable or single item
            if not reasons and amt >= 3.0 * overall_median and (amt - overall_median) >= 3000:
                mult = round(amt / overall_median, 1) if overall_median > 0 else 0
                reasons.append(
                    f"{mult}x higher than overall median {t_type} (₹{overall_median:,.2f})"
                )

            if reasons:
                anomalies.append(
                    UnusualTransaction(
                        id=row_id,
                        date=row["date"].strftime("%Y-%m-%d"),
                        description=str(row["description"]),
                        amount=round(amt, 2),
                        type=t_type,
                        category=cat,
                        reason="; ".join(reasons),
                        ratio_to_category_avg=ratio_cat,
                        severity=severity,
                    )
                )

    # Sort anomalies descending by amount
    anomalies.sort(key=lambda x: x.amount, reverse=True)

    summary = (
        f"Detected {len(anomalies)} unusual transaction(s) requiring review based on category variance and statistical deviation."
        if anomalies
        else "No statistical anomalies detected; transactions conform to normal spending and income baselines."
    )

    return AnomalyReport(
        total_anomalies=len(anomalies),
        anomalies=anomalies,
        summary=summary,
    )

