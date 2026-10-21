# E-commerce Fulfillment & Delivery Exception Intelligence

## Decision memo

### Executive summary

This analysis uses a synthetic e-commerce fulfillment dataset. All delivery-rate calculations below use delivered orders as the denominator. The findings describe patterns in the simulated data; they are not evidence of actual Amazon operational performance.

### Overall performance

- Delivered orders analyzed: **4,712**
- Late delivered orders: **907**
- Late-delivery rate among delivered orders: **19.25%**
- Highest observed carrier late rate: **Carrier_3 (28.12%)** across 1,138 delivered orders.

### Operational segments to investigate

The table below includes segments with at least 100 delivered orders, reducing the chance of prioritizing a segment solely because of a small sample.

| Carrier | Fulfillment center | Shipping mode | Delivered orders | Late orders | Late rate |
|---|---|---|---:|---:|---:|
| Carrier_3 | FC_D | Standard | 147 | 58 | 39.46% |
| Carrier_3 | FC_C | Standard | 158 | 45 | 28.48% |
| Carrier_3 | FC_B | Standard | 199 | 55 | 27.64% |
| Carrier_3 | FC_A | Expedited | 108 | 26 | 24.07% |
| Carrier_3 | FC_A | Standard | 209 | 50 | 23.92% |
| Carrier_1 | FC_D | Standard | 186 | 44 | 23.66% |
| Carrier_2 | FC_D | Standard | 162 | 35 | 21.60% |
| Carrier_1 | FC_C | Standard | 227 | 38 | 16.74% |
| Carrier_4 | FC_A | Standard | 143 | 22 | 15.38% |
| Carrier_1 | FC_B | Standard | 245 | 37 | 15.10% |

### Recommended next steps

1. **Investigate the highest-rate carrier.** Review delivery handoffs, promised-date accuracy, route mix, and delay reasons before deciding whether a carrier-level intervention is warranted.
2. **Validate the operational context.** Compare carrier performance within shipping modes and fulfillment centers; overall averages may hide differences in the orders handled.
3. **Monitor both rate and volume.** Track late-order counts, delivered-order denominators, average delay, and segment sample sizes over time.
4. **Test changes before scaling.** Use a controlled pilot or appropriate operational evaluation to determine whether an intervention actually improves delivery performance.

### Hypothetical improvement scenario

The scenario assumes a **10.00% relative reduction** in late orders for Carrier_3. Under that assumption, the estimated number of fewer late orders is **32**, and the estimated overall late-delivery rate would be **18.57%**.

**Important:** This is a hypothetical calculation, not a forecast or a measured outcome. It does not prove causality, guarantee improvement, or estimate financial savings.

### Limitations

- The dataset is synthetic and does not represent actual company data.
- The observed associations do not establish that a carrier or fulfillment center caused delays.
- The scenario depends on an assumed relative reduction and should be validated with real operational evidence.
- Results should be re-evaluated when additional data, delay reasons, and time-based trends are available.
