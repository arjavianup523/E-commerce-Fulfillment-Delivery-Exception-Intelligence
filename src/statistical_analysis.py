
from pathlib import Path
import sqlite3

import pandas as pd
from scipy.stats import chi2_contingency


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "fulfillment.db"
OUTPUT_DIR = ROOT / "reports" / "statistical_analysis"


def load_orders() -> pd.DataFrame:
    """Load delivered orders so every delivery-rate denominator is consistent."""
    with sqlite3.connect(DB_PATH) as connection:
        df = pd.read_sql_query(
            """
            SELECT
                carrier,
                fulfillment_center,
                shipping_mode,
                late_delivery,
                delay_days,
                shipping_cost
            FROM orders
            WHERE delivery_status = 'Delivered'
            """,
            connection,
        )

    if df.empty:
        raise ValueError("No delivered orders were found in the database.")

    df["late_delivery"] = df["late_delivery"].astype(int)
    return df


def wilson_interval(successes: int, total: int, z: float = 1.96):
    """Calculate a 95% Wilson confidence interval for a proportion."""
    if total <= 0:
        return float("nan"), float("nan")

    proportion = successes / total
    denominator = 1 + (z**2 / total)

    center = (
        proportion + (z**2 / (2 * total))
    ) / denominator

    margin = (
        z
        * (
            proportion * (1 - proportion) / total
            + z**2 / (4 * total**2)
        ) ** 0.5
        / denominator
    )

    return (
        max(0.0, center - margin) * 100,
        min(1.0, center + margin) * 100,
    )


def build_carrier_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Summarize delivered-order late rates and confidence intervals by carrier."""
    summary = (
        df.groupby("carrier", as_index=False)
        .agg(
            delivered_orders=("late_delivery", "size"),
            late_orders=("late_delivery", "sum"),
            average_shipping_cost=("shipping_cost", "mean"),
            average_delay_days=("delay_days", "mean"),
            late_rate=("late_delivery", "mean"),
        )
    )

    summary["late_rate"] *= 100

    intervals = summary.apply(
        lambda row: wilson_interval(
            int(row["late_orders"]),
            int(row["delivered_orders"]),
        ),
        axis=1,
    )

    summary["ci_lower"] = [interval[0] for interval in intervals]
    summary["ci_upper"] = [interval[1] for interval in intervals]

    numeric_columns = [
        "average_shipping_cost",
        "average_delay_days",
        "late_rate",
        "ci_lower",
        "ci_upper",
    ]
    summary[numeric_columns] = summary[numeric_columns].round(2)

    return summary.sort_values("late_rate", ascending=False)


def build_mode_adjusted_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Compare carriers within each shipping mode."""
    summary = (
        df.groupby(["shipping_mode", "carrier"], as_index=False)
        .agg(
            delivered_orders=("late_delivery", "size"),
            late_orders=("late_delivery", "sum"),
            average_delay_days=("delay_days", "mean"),
            average_shipping_cost=("shipping_cost", "mean"),
            late_rate=("late_delivery", "mean"),
        )
    )

    summary["late_rate"] *= 100
    summary["late_rate"] = summary["late_rate"].round(2)
    summary["average_delay_days"] = summary["average_delay_days"].round(2)
    summary["average_shipping_cost"] = summary["average_shipping_cost"].round(2)

    return summary.sort_values(
        ["shipping_mode", "late_rate"],
        ascending=[True, False],
    )


def run_association_test(df: pd.DataFrame) -> pd.DataFrame:
    """Test whether carrier and late-delivery outcome are associated."""
    contingency = pd.crosstab(df["carrier"], df["late_delivery"])

    if contingency.shape[0] < 2 or contingency.shape[1] < 2:
        raise ValueError(
            "The chi-square test requires at least two carriers "
            "and both late and on-time delivered orders."
        )

    chi2, p_value, degrees_of_freedom, expected = chi2_contingency(
        contingency
    )

    result = pd.DataFrame(
        [
            {
                "test": "Chi-square test of independence",
                "observations": int(contingency.to_numpy().sum()),
                "chi_square_statistic": round(float(chi2), 4),
                "degrees_of_freedom": int(degrees_of_freedom),
                "p_value": float(p_value),
                "minimum_expected_cell_count": round(
                    float(expected.min()), 2
                ),
                "interpretation": (
                    "Evidence of association between carrier and "
                    "late-delivery outcome among delivered orders."
                    if p_value < 0.05
                    else
                    "Insufficient evidence of an association at the 5% level."
                ),
                "causal_claim": False,
            }
        ]
    )

    return result


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = load_orders()

    carrier_summary = build_carrier_summary(df)
    mode_summary = build_mode_adjusted_summary(df)
    association_result = run_association_test(df)

    carrier_path = OUTPUT_DIR / "carrier_confidence_intervals.csv"
    mode_path = OUTPUT_DIR / "carrier_by_shipping_mode.csv"
    association_path = OUTPUT_DIR / "carrier_association_test.csv"

    carrier_summary.to_csv(carrier_path, index=False)
    mode_summary.to_csv(mode_path, index=False)
    association_result.to_csv(association_path, index=False)

    print(f"Delivered orders analyzed: {len(df):,}")
    print(f"Overall late-delivery rate: {df['late_delivery'].mean():.2%}")

    print("\nCarrier confidence intervals:")
    print(carrier_summary.to_string(index=False))

    print("\nCarrier performance by shipping mode:")
    print(mode_summary.to_string(index=False))

    print("\nCarrier association test:")
    print(association_result.to_string(index=False))

    print(f"\nReports saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
