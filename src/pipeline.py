from pathlib import Path
import json
import pandas as pd
from src.generate_data import generate_orders
from src.analysis import validate_orders, add_metrics, segment_summary, write_sqlite
from src.simulate import simulate_targeted_intervention

ROOT = Path(__file__).resolve().parents[1]

def main():
    data_dir, report_dir = ROOT / "data", ROOT / "reports"
    data_dir.mkdir(exist_ok=True)
    report_dir.mkdir(exist_ok=True)
    raw = generate_orders(n=5000, seed=42)
    raw.to_csv(data_dir / "orders.csv", index=False)
    checks = validate_orders(raw)
    (report_dir / "data_quality_checks.json").write_text(json.dumps(checks, indent=2))
    df = add_metrics(raw)
    df.to_csv(data_dir / "orders_analyzed.csv", index=False)
    write_sqlite(df, data_dir / "fulfillment.db")

    for segment in ["carrier", "fulfillment_center", "region", "shipping_mode", "exception_type"]:
        segment_summary(df, segment).to_csv(report_dir / f"late_delivery_by_{segment}.csv", index=False)

    top_carrier = segment_summary(df, "carrier").iloc[0]["carrier"]
    scenario = simulate_targeted_intervention(df, str(top_carrier), 0.20)
    (report_dir / "intervention_scenario.json").write_text(json.dumps(scenario, indent=2))

    delivered = df[df["delivery_status"].eq("Delivered")]
    top_region = segment_summary(df, "region").iloc[0]
    memo = f"""# Fulfillment Decision Memo (Synthetic Data)

## Scope
Generated {len(df):,} synthetic orders with seed 42. These are not Amazon data or measured operational outcomes.

## Quality gate
- Duplicate order IDs: {checks['duplicate_order_ids']}
- Missing order IDs: {checks['missing_order_ids']}
- Negative order values: {checks['negative_order_values']}
- Negative shipping costs: {checks['negative_shipping_costs']}
- Delivered orders without actual delivery date: {checks['delivered_without_actual_date']}
- Quality checks passed: {checks['passed']}

## Baseline
- Delivered orders: {len(delivered):,}
- Late delivered orders: {int(delivered['late_delivery'].sum()):,}
- Overall late-delivery rate: {delivered['late_delivery'].mean():.1%}
- Highest observed region late rate: {top_region['region']} ({top_region['late_rate']:.1%}; n={int(top_region['orders'])})

## Scenario, not forecast
An illustrative 20% relative reduction in late orders for the highest-late-rate carrier segment would move late orders from {scenario['late_orders_before']:,} to {scenario['late_orders_after_scenario']:,} under the stated assumption. This is not a causal estimate and does not establish cost savings.

## Recommended next steps
1. Validate segment differences with confidence intervals and minimum sample-size rules.
2. Check time trends and adjust for shipping mode, order value, region, and fulfillment center before interpreting segment effects.
3. Interview operations stakeholders and verify exception codes against operational definitions.
4. Run a small controlled pilot before claiming an intervention works.
5. Quantify cost impact only after obtaining defensible cost-per-failure and intervention-cost inputs.
"""
    (report_dir / "decision_memo.md").write_text(memo)
    print(f"Generated {len(df):,} synthetic orders.")
    print(f"Data quality passed: {checks['passed']}")
    print(f"Overall late-delivery rate: {delivered['late_delivery'].mean():.1%}")
    print(f"Outputs: {report_dir}")

if __name__ == "__main__":
    main()
