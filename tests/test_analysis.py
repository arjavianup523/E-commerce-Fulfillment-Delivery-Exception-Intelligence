import pandas as pd
import pytest
from src.generate_data import generate_orders
from src.analysis import validate_orders, add_metrics, segment_summary
from src.simulate import simulate_targeted_intervention

def test_generator_is_reproducible():
    pd.testing.assert_frame_equal(generate_orders(100, 7), generate_orders(100, 7))

def test_order_ids_unique():
    df = generate_orders(250, 1)
    assert df["order_id"].is_unique

def test_quality_checks_pass_on_generated_data():
    assert validate_orders(generate_orders(500, 4))["passed"]

def test_late_flag_matches_date_comparison():
    df = add_metrics(generate_orders(500, 3))
    expected = ((df["delivery_status"] == "Delivered") &
                (df["actual_delivery_date"] > df["promised_delivery_date"])).astype(int)
    assert (df["late_delivery"] == expected).all()

def test_segment_summary_late_rate_bounded():
    df = add_metrics(generate_orders(500, 5))
    summary = segment_summary(df, "carrier")
    assert summary["late_rate"].between(0, 1).all()
    assert (summary["orders"] >= summary["late_orders"]).all()

def test_simulation_never_increases_late_orders():
    df = add_metrics(generate_orders(500, 5))
    result = simulate_targeted_intervention(df, "Carrier_3", 0.2)
    assert result["late_orders_after_scenario"] <= result["late_orders_before"]

def test_invalid_scenario_rejected():
    df = add_metrics(generate_orders(100, 5))
    with pytest.raises(ValueError):
        simulate_targeted_intervention(df, "Carrier_1", 1.2)
