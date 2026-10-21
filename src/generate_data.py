from pathlib import Path
import numpy as np
import pandas as pd

def generate_orders(n: int = 5000, seed: int = 42) -> pd.DataFrame:
    """Generate reproducible synthetic e-commerce orders; not real company data."""
    rng = np.random.default_rng(seed)
    order_date = pd.to_datetime("2025-01-01") + pd.to_timedelta(
        rng.integers(0, 365, size=n), unit="D"
    )
    regions = np.array(["North", "South", "East", "West", "Central"])
    centers = np.array(["FC_A", "FC_B", "FC_C", "FC_D"])
    carriers = np.array(["Carrier_1", "Carrier_2", "Carrier_3", "Carrier_4"])
    modes = np.array(["Standard", "Expedited", "SameDay"])

    region = rng.choice(regions, n, p=[.22, .24, .16, .23, .15])
    fc = rng.choice(centers, n, p=[.30, .27, .23, .20])
    carrier = rng.choice(carriers, n, p=[.31, .29, .23, .17])
    mode = rng.choice(modes, n, p=[.65, .27, .08])
    category = rng.choice(["Home", "Electronics", "Apparel", "Beauty", "Grocery"], n)
    order_value = np.round(np.clip(rng.lognormal(mean=7.0, sigma=.65, size=n), 100, 50000), 2)

    promised_days = np.select([mode == "SameDay", mode == "Expedited"], [1, 2], default=5)
    # Delay probability includes intentionally synthetic segment effects.
    p_late = np.full(n, .13)
    p_late += np.where(carrier == "Carrier_3", .12, 0)
    p_late += np.where(fc == "FC_D", .08, 0)
    p_late += np.where(region == "East", .04, 0)
    p_late += np.where(mode == "SameDay", .06, 0)
    p_late = np.clip(p_late, .04, .65)
    late = rng.random(n) < p_late
    delay_days = np.where(late, rng.choice([1, 2, 3, 5], n, p=[.54, .27, .14, .05]), 0)
    early_days = np.where(~late, rng.choice([0, 1, 2], n, p=[.72, .22, .06]), 0)
    actual_delta = np.where(late, promised_days + delay_days, np.maximum(0, promised_days - early_days))
    actual_date = order_date + pd.to_timedelta(actual_delta, unit="D")
    promised_date = order_date + pd.to_timedelta(promised_days, unit="D")
    ship_cost = np.round(
        np.maximum(25, 65 + .008 * order_value + np.where(mode == "SameDay", 90, np.where(mode == "Expedited", 45, 0))
                   + rng.normal(0, 18, n)), 2
    )
    status = rng.choice(["Delivered", "In Transit", "Cancelled"], n, p=[.94, .045, .015])
    # Dates for non-delivered orders are intentionally blank.
    actual_date = pd.Series(actual_date).where(status == "Delivered", pd.NaT)
    late_flag = ((actual_date > promised_date) & (status == "Delivered")).astype(int)
    exception = np.where(status == "Cancelled", "Cancellation",
                 np.where(status != "Delivered", "In Transit",
                 np.where(late_flag == 1,
                          rng.choice(["Carrier Delay", "FC Processing", "Weather/Route", "Other"], n,
                                     p=[.45, .25, .20, .10]), "None")))
    df = pd.DataFrame({
        "order_id": [f"ORD{i:06d}" for i in range(1, n + 1)],
        "order_date": order_date,
        "region": region,
        "fulfillment_center": fc,
        "carrier": carrier,
        "shipping_mode": mode,
        "category": category,
        "order_value": order_value,
        "shipping_cost": ship_cost,
        "promised_delivery_date": promised_date,
        "actual_delivery_date": actual_date,
        "delivery_status": status,
        "exception_type": exception,
    })
    return df

if __name__ == "__main__":
    out = Path("data")
    out.mkdir(exist_ok=True)
    generate_orders().to_csv(out / "orders.csv", index=False)
    print(f"Wrote {out / 'orders.csv'}")
