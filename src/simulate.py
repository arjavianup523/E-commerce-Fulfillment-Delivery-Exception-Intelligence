import pandas as pd

def simulate_targeted_intervention(df: pd.DataFrame, target_carrier: str,
                                   assumed_relative_reduction: float = 0.20) -> dict:
    """Illustrative scenario only: assume targeted late orders are reduced by a chosen fraction."""
    if not 0 <= assumed_relative_reduction <= 1:
        raise ValueError("assumed_relative_reduction must be between 0 and 1")
    delivered = df[df["delivery_status"].eq("Delivered")]
    late_before = int(delivered["late_delivery"].sum())
    target_mask = delivered["carrier"].eq(target_carrier)
    target_late = int(delivered.loc[target_mask, "late_delivery"].sum())
    assumed_prevented = int(round(target_late * assumed_relative_reduction))
    late_after = late_before - assumed_prevented
    n_delivered = len(delivered)
    return {
        "target_carrier": target_carrier,
        "assumed_relative_reduction": assumed_relative_reduction,
        "delivered_orders": int(n_delivered),
        "late_orders_before": late_before,
        "target_segment_late_orders": target_late,
        "assumed_late_orders_prevented": assumed_prevented,
        "late_orders_after_scenario": late_after,
        "late_rate_before": late_before / max(1, n_delivered),
        "late_rate_after_scenario": late_after / max(1, n_delivered),
        "interpretation": "Illustrative scenario under an explicit assumption; not causal evidence or realized savings."
    }
