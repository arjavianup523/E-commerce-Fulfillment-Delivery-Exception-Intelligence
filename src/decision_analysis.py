
from pathlib import Path
import json
import sqlite3

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "fulfillment.db"
OUTPUT_DIR = ROOT / "reports" / "decision_analysis"
OUTPUT_PATH = OUTPUT_DIR / "improvement_scenario.json"

# Hypothetical assumption: reduce late deliveries for the selected carrier
# by 10% relative to its current late-order count.
TARGET_RELATIVE_REDUCTION = 0.10


def load_delivered_orders() -> pd.DataFrame:
    with sqlite3.connect(DB_PATH) as connection:
        df = pd.read_sql_query(
            """
            SELECT
                carrier,
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


def calculate_scenario(df: pd.DataFrame) -> dict:
    delivered_orders = int(len(df))
    baseline_late_orders = int(df["late_delivery"].sum())
    baseline_late_rate = baseline_late_orders / delivered_orders

    carrier_summary = (
        df.groupby("carrier", as_index=False)
        .agg(
            delivered_orders=("late_delivery", "size"),
            late_orders=("late_delivery", "sum"),
        )
    )
    carrier_summary["late_rate"] = (
        carrier_summary["late_orders"] / carrier_summary["delivered_orders"]
    )

    # Choose the carrier with the highest observed late-delivery rate.
    target = carrier_summary.sort_values(
        ["late_rate", "delivered_orders"],
        ascending=[False, False],
    ).iloc[0]

    target_carrier = str(target["carrier"])
    target_delivered_orders = int(target["delivered_orders"])
    target_baseline_late_orders = int(target["late_orders"])
    target_baseline_rate = float(target["late_rate"])

    estimated_fewer_late_orders = int(
        round(target_baseline_late_orders * TARGET_RELATIVE_REDUCTION)
    )

    estimated_total_late_orders = max(
        0,
        baseline_late_orders - estimated_fewer_late_orders,
    )
    estimated_overall_late_rate = (
        estimated_total_late_orders / delivered_orders
    )

    return {
        "analysis_type": "hypothetical_scenario",
        "dataset": "synthetic_e-commerce_fulfillment_data",
        "denominator": "delivered_orders_only",
        "delivered_orders": delivered_orders,
        "baseline_late_orders": baseline_late_orders,
        "baseline_late_rate_pct": round(baseline_late_rate * 100, 2),
        "target_carrier": target_carrier,
        "target_carrier_delivered_orders": target_delivered_orders,
        "target_carrier_baseline_late_orders": target_baseline_late_orders,
        "target_carrier_baseline_late_rate_pct": round(
            target_baseline_rate * 100, 2
        ),
        "assumed_relative_reduction_pct": round(
            TARGET_RELATIVE_REDUCTION * 100, 2
        ),
        "estimated_fewer_late_orders": estimated_fewer_late_orders,
        "estimated_total_late_orders_after_scenario": estimated_total_late_orders,
        "estimated_overall_late_rate_after_scenario_pct": round(
            estimated_overall_late_rate * 100, 2
        ),
        "estimated_overall_rate_improvement_percentage_points": round(
            (baseline_late_rate - estimated_overall_late_rate) * 100, 2
        ),
        "interpretation": (
            "Illustrative scenario only. It assumes the selected carrier's "
            "late-order count falls by the stated relative percentage. "
            "It does not establish causality, guarantee improvement, or "
            "estimate financial savings."
        ),
    }


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = load_delivered_orders()
    scenario = calculate_scenario(df)

    with OUTPUT_PATH.open("w", encoding="utf-8") as file:
        json.dump(scenario, file, indent=4)

    print("Hypothetical improvement scenario")
    print(f"Delivered orders: {scenario['delivered_orders']:,}")
    print(
        "Baseline late-delivery rate: "
        f"{scenario['baseline_late_rate_pct']:.2f}%"
    )
    print(f"Target carrier: {scenario['target_carrier']}")
    print(
        "Target carrier baseline late rate: "
        f"{scenario['target_carrier_baseline_late_rate_pct']:.2f}%"
    )
    print(
        "Assumed relative reduction: "
        f"{scenario['assumed_relative_reduction_pct']:.2f}%"
    )
    print(
        "Estimated fewer late orders: "
        f"{scenario['estimated_fewer_late_orders']:,}"
    )
    print(
        "Estimated overall late rate after scenario: "
        f"{scenario['estimated_overall_late_rate_after_scenario_pct']:.2f}%"
    )
    print(f"\nScenario saved to: {OUTPUT_PATH}")
    print(scenario["interpretation"])


if __name__ == "__main__":
    main()
