# E-commerce Fulfillment & Delivery Exception Intelligence

A Python, SQL, and statistical analysis project for identifying delivery exceptions, comparing carrier and fulfillment-center performance, and evaluating hypothetical operational improvements.

## Business Problem

Late deliveries can affect customer experience and operational performance. Business analysts need to identify where delays are concentrated, distinguish high-risk segments from small-sample fluctuations, and recommend investigations supported by data.

This project simulates an e-commerce fulfillment operation and builds a reproducible analysis pipeline to investigate those questions.

**Data disclaimer:** All order data is synthetic. This project does not use Amazon internal data and does not measure actual Amazon operational performance.

## Business Questions

- What proportion of delivered orders arrived after their promised delivery date?
- Which carriers have the highest observed late-delivery rates?
- How does delivery performance vary across fulfillment centers?
- Do carrier performance patterns differ by shipping mode?
- Which operational segments warrant further investigation?
- What would a hypothetical reduction in late orders mean for overall delivery performance?

## Technical Stack

- **Python:** data generation, transformation, validation, analysis, and scenario calculations
- **Pandas and NumPy:** data processing and numerical analysis
- **SQL and SQLite:** querying operational data and producing segment-level summaries
- **SciPy:** chi-square statistical testing
- **Statistical methods:** Wilson confidence intervals and tests of association
- **Pytest:** automated testing
- **Git and GitHub:** version control and project documentation

## Project Workflow

1. Generate 5,000 synthetic e-commerce orders using a reproducible random seed.
2. Validate the dataset and calculate delivery metrics, including late-delivery flags and delay days.
3. Store structured order data in SQLite.
4. Run SQL analyses across overall performance, carriers, fulfillment centers, and operational segments.
5. Calculate carrier-level Wilson confidence intervals and compare carrier performance within shipping modes.
6. Test the association between carrier and late-delivery outcome among delivered orders.
7. Evaluate a clearly labeled hypothetical improvement scenario.
8. Generate a decision memo with findings, investigation priorities, and limitations.
9. Run automated tests to check project behavior.

## Key Findings

Results below are from the current synthetic dataset and generated reports.

| Metric | Result |
|---|---:|
| Synthetic orders generated | 5,000 |
| Delivered orders analyzed | 4,712 |
| Late delivered orders | 907 |
| Late-delivery rate among delivered orders | 19.25% |
| Carrier_3 late-delivery rate | 28.12% |
| Carrier_2 late-delivery rate | 15.66% |
| Highest-rate identified segment | Carrier_3 / FC_D / Standard |
| Delivered orders in that segment | 147 |
| Late-delivery rate in that segment | 39.46% |

### Statistical Analysis

Carrier_3 had the highest overall observed late-delivery rate in this generated dataset. Its estimated 95% Wilson confidence interval was 25.58%–30.80%.

A chi-square test of independence found an association between carrier and late-delivery outcome among delivered orders:

- Chi-square statistic: 76.7357
- Degrees of freedom: 3
- p-value: approximately 1.54 × 10⁻¹⁶
- Observations: 4,712 delivered orders

This result indicates evidence of an association in the simulated data. It does not establish that carrier choice caused late deliveries. Differences in order mix, shipping mode, fulfillment center, or other factors may contribute to the observed patterns.

### Hypothetical Improvement Scenario

The scenario assumes a 10% relative reduction in late orders for Carrier_3.

Under that assumption, the model estimates approximately 32 fewer late orders and an overall late-delivery rate of 18.57%, compared with the baseline of 19.25%.

This is an illustrative calculation, not a measured outcome, causal estimate, guaranteed improvement, or financial-savings estimate.

## Business Recommendations

1. **Investigate carrier-level variation.** Review delivery handoffs, route mix, promised-date accuracy, and delay reasons for the highest-rate carrier.
2. **Examine operational segments.** Prioritize combinations of carrier, fulfillment center, and shipping mode with elevated late-delivery rates and meaningful sample sizes.
3. **Compare like with like.** Review carrier performance within shipping modes and fulfillment centers before making operational decisions.
4. **Monitor rates and volumes together.** Track late-order counts, delivered-order denominators, average delay, and confidence intervals.
5. **Validate interventions.** Run an appropriate pilot and compare results before scaling any proposed change.

## Repository Structure

```text
E-commerce Fulfillment & Delivery Exception Intelligence/
├── src/
│   ├── generate_data.py
│   ├── analysis.py
│   ├── pipeline.py
│   ├── run_sql_analysis.py
│   ├── statistical_analysis.py
│   ├── decision_analysis.py
│   └── decision_memo.py
├── sql/
│   └── analysis_queries.sql
├── tests/
├── data/
│   └── fulfillment.db
├── reports/
│   ├── sql_analysis/
│   ├── statistical_analysis/
│   ├── decision_analysis/
│   └── decision_memo.md
└── README.md
```

## Run Locally

### 1. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

Install the dependencies listed in `requirements.txt`:

```powershell
python -m pip install -r requirements.txt
```

### 3. Run the pipeline and analyses

Run these commands from the repository root:

```powershell
python -m pytest -q
python -m src.pipeline
python -m src.run_sql_analysis
python -m src.statistical_analysis
python -m src.decision_analysis
python -m src.decision_memo
```

The pipeline generates the synthetic data and refreshes the database before the downstream analyses run.

## Testing

The current automated test suite passes **7 tests**. Run `python -m pytest -q` to verify the code in your environment.

## Limitations

- The dataset is synthetic and may not reflect real-world delivery distributions.
- Findings describe the generated data, not an actual company's operations.
- Statistical association does not prove causality.
- Hypothetical scenario outputs depend on explicitly stated assumptions.
- No real financial savings or operational improvements are claimed.

## Skills Demonstrated

Python · SQL · Pandas · NumPy · SQLite · Statistical Analysis · Data Quality Validation · Root-Cause Investigation · Operational Metrics · Scenario Analysis · Business Recommendations · Automated Testing
