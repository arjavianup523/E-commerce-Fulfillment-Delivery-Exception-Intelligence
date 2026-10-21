
from pathlib import Path
import json
import sqlite3

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "fulfillment.db"
SCENARIO_PATH = (
    ROOT / "reports" / "decision_analysis" / "improvement_scenario.json"
)
OUTPUT_PATH = ROOT / "reports" / "decision_memo.md"

MIN_SEGMENT_SIZE = 100


def load_delivered_orders() -> pd.DataFrame:
    with sqlite3.connect(DB_PATH) as connection:
        df = pd.read_sql_query(
            """
            SELECT
                carrier,
                fulfillment_center,
                shipping_mode,
                late_delivery,
                delay_days
            FROM orders
            WHERE delivery_status = 'Delivered'
            """,
            connection,
        )

    if df.empty:
        raise ValueError("No delivered orders were found in the database.")

    df["late_delivery"] = df["late_delivery"].astype(int)
    return df


def load_scenario() -> dict:
    if not SCENARIO_PATH.exists():
        raise FileNotFoundError(
            f"Scenario file not found: {SCENARIO_PATH}\n"
            "Run `python -m src.decision_analysis` first."
        )

    with SCENARIO_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def build_segment_summary(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby(
            ["carrier", "fulfillment_center", "shipping_mode"],
            as_index=False,
        )
        .agg(
            delivered_orders=("late_delivery", "size"),
            late_orders=("late_delivery", "sum"),
            average_delay_days=("delay_days", "mean"),
        )
    )

    summary["late_rate_pct"] = (
        summary["late_orders"] / summary["delivered_orders"] * 100
    )

    eligible = summary[
        summary["delivered_orders"] >= MIN_SEGMENT_SIZE
    ].copy()

    return eligible.sort_values(
        ["late_rate_pct", "delivered_orders"],
        ascending=[False, False],
    )


def build_memo(df: pd.DataFrame, scenario: dict) -> str:
    delivered_orders = len(df)
    late_orders = int(df["late_delivery"].sum())
    late_rate_pct = df["late_delivery"].mean() * 100

    carrier_summary = (
        df.groupby("carrier", as_index=False)
        .agg(
            delivered_orders=("late_delivery", "size"),
            late_orders=("late_delivery", "sum"),
        )
    )
    carrier_summary["late_rate_pct"] = (
        carrier_summary["late_orders"]
        / carrier_summary["delivered_orders"]
        * 100
    )
    carrier_summary = carrier_summary.sort_values(
        ["late_rate_pct", "delivered_orders"],
        ascending=[False, False],
    )

    highest_carrier = carrier_summary.iloc[0]
    segments = build_segment_summary(df)

    lines = [
        "# E-commerce Fulfillment & Delivery Exception Intelligence",
        "",
        "## Decision memo",
        "",
        "### Executive summary",
        "",
        (
            "This analysis uses a synthetic e-commerce fulfillment dataset. "
            "All delivery-rate calculations below use delivered orders as "
            "the denominator. The findings describe patterns in the "
            "simulated data; they are not evidence of actual Amazon "
            "operational performance."
        ),
        "",
        "### Overall performance",
        "",
        f"- Delivered orders analyzed: **{delivered_orders:,}**",
        f"- Late delivered orders: **{late_orders:,}**",
        f"- Late-delivery rate among delivered orders: **{late_rate_pct:.2f}%**",
        (
            f"- Highest observed carrier late rate: "
            f"**{highest_carrier['carrier']} "
            f"({highest_carrier['late_rate_pct']:.2f}%)** "
            f"across {int(highest_carrier['delivered_orders']):,} "
            "delivered orders."
        ),
        "",
        "### Operational segments to investigate",
        "",
        (
            f"The table below includes segments with at least "
            f"{MIN_SEGMENT_SIZE} delivered orders, reducing the chance "
            "of prioritizing a segment solely because of a small sample."
        ),
        "",
        "| Carrier | Fulfillment center | Shipping mode | Delivered orders | Late orders | Late rate |",
        "|---|---|---|---:|---:|---:|",
    ]

    if segments.empty:
        lines.append("| No qualifying segments | — | — | — | — | — |")
    else:
        for _, row in segments.head(10).iterrows():
            lines.append(
                f"| {row['carrier']} "
                f"| {row['fulfillment_center']} "
                f"| {row['shipping_mode']} "
                f"| {int(row['delivered_orders']):,} "
                f"| {int(row['late_orders']):,} "
                f"| {row['late_rate_pct']:.2f}% |"
            )

    lines.extend(
        [
            "",
            "### Recommended next steps",
            "",
            "1. **Investigate the highest-rate carrier.** Review delivery "
            "handoffs, promised-date accuracy, route mix, and delay reasons "
            "before deciding whether a carrier-level intervention is warranted.",
            "2. **Validate the operational context.** Compare carrier "
            "performance within shipping modes and fulfillment centers; "
            "overall averages may hide differences in the orders handled.",
            "3. **Monitor both rate and volume.** Track late-order counts, "
            "delivered-order denominators, average delay, and segment sample "
            "sizes over time.",
            "4. **Test changes before scaling.** Use a controlled pilot or "
            "appropriate operational evaluation to determine whether an "
            "intervention actually improves delivery performance.",
            "",
            "### Hypothetical improvement scenario",
            "",
            (
                f"The scenario assumes a **"
                f"{scenario['assumed_relative_reduction_pct']:.2f}% "
                "relative reduction** in late orders for "
                f"{scenario['target_carrier']}. Under that assumption, "
                f"the estimated number of fewer late orders is "
                f"**{scenario['estimated_fewer_late_orders']:,}**, and "
                "the estimated overall late-delivery rate would be "
                f"**{scenario['estimated_overall_late_rate_after_scenario_pct']:.2f}%**."
            ),
            "",
            (
                "**Important:** This is a hypothetical calculation, not a "
                "forecast or a measured outcome. It does not prove causality, "
                "guarantee improvement, or estimate financial savings."
            ),
            "",
            "### Limitations",
            "",
            "- The dataset is synthetic and does not represent actual company data.",
            "- The observed associations do not establish that a carrier or fulfillment center caused delays.",
            "- The scenario depends on an assumed relative reduction and should be validated with real operational evidence.",
            "- Results should be re-evaluated when additional data, delay reasons, and time-based trends are available.",
            "",
        ]
    )

    return "\n".join(lines)


def main():
    df = load_delivered_orders()
    scenario = load_scenario()

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    memo = build_memo(df, scenario)
    OUTPUT_PATH.write_text(memo, encoding="utf-8")

    print(f"Decision memo saved to: {OUTPUT_PATH}")
    print("\n" + memo)


if __name__ == "__main__":
    main()
