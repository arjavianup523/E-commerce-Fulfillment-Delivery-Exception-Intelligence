from pathlib import Path
import sqlite3
import pandas as pd

DATE_COLS = ["order_date", "promised_delivery_date", "actual_delivery_date"]

def validate_orders(df: pd.DataFrame) -> dict:
    required = {
        "order_id", "order_date", "region", "fulfillment_center", "carrier",
        "shipping_mode", "order_value", "shipping_cost", "promised_delivery_date",
        "actual_delivery_date", "delivery_status", "exception_type"
    }
    missing_cols = sorted(required - set(df.columns))
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    checks = {
        "row_count": int(len(df)),
        "duplicate_order_ids": int(df["order_id"].duplicated().sum()),
        "missing_order_ids": int(df["order_id"].isna().sum()),
        "negative_order_values": int((df["order_value"] < 0).sum()),
        "negative_shipping_costs": int((df["shipping_cost"] < 0).sum()),
        "delivered_without_actual_date": int(((df["delivery_status"] == "Delivered") & df["actual_delivery_date"].isna()).sum()),
        "actual_before_order": int((pd.to_datetime(df["actual_delivery_date"], errors="coerce") < pd.to_datetime(df["order_date"], errors="coerce")).sum()),
    }
    checks["passed"] = all(v == 0 for k, v in checks.items() if k not in {"row_count", "passed"})
    return checks

def add_metrics(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["order_date"] = pd.to_datetime(out["order_date"], errors="coerce")
    out["promised_delivery_date"] = pd.to_datetime(out["promised_delivery_date"], errors="coerce")
    out["actual_delivery_date"] = pd.to_datetime(out["actual_delivery_date"], errors="coerce")
    delivered = out["delivery_status"].eq("Delivered")
    out["late_delivery"] = (
        delivered & out["actual_delivery_date"].notna() &
        (out["actual_delivery_date"] > out["promised_delivery_date"])
    ).astype(int)
    out["delay_days"] = 0
    late_mask = out["late_delivery"].eq(1)
    out.loc[late_mask, "delay_days"] = (
        out.loc[late_mask, "actual_delivery_date"] - out.loc[late_mask, "promised_delivery_date"]
    ).dt.days
    out["order_month"] = out["order_date"].dt.to_period("M").astype(str)
    return out

def segment_summary(df: pd.DataFrame, segment: str) -> pd.DataFrame:
    delivered = df[df["delivery_status"].eq("Delivered")].copy()
    summary = (delivered.groupby(segment, dropna=False)
        .agg(orders=("order_id", "count"),
             late_orders=("late_delivery", "sum"),
             avg_shipping_cost=("shipping_cost", "mean"),
             avg_order_value=("order_value", "mean"),
             avg_delay_days=("delay_days", "mean"))
        .reset_index())
    summary["late_rate"] = summary["late_orders"] / summary["orders"].clip(lower=1)
    return summary.sort_values(["late_rate", "orders"], ascending=[False, False])

def write_sqlite(df: pd.DataFrame, db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as con:
        df.to_sql("orders", con, if_exists="replace", index=False)
