
-- Query 1: Overall delivery performance
-- The denominator includes delivered orders only.
SELECT
    COUNT(*) AS delivered_orders,
    SUM(late_delivery) AS late_orders,
    ROUND(100.0 * AVG(late_delivery), 2) AS late_rate_pct,
    ROUND(AVG(delay_days), 2) AS avg_delay_days,
    ROUND(SUM(shipping_cost), 2) AS total_shipping_cost
FROM orders
WHERE delivery_status = 'Delivered';


-- Query 2: Delivery performance by carrier
SELECT
    carrier,
    COUNT(*) AS delivered_orders,
    SUM(late_delivery) AS late_orders,
    ROUND(100.0 * AVG(late_delivery), 2) AS late_rate_pct,
    ROUND(AVG(delay_days), 2) AS avg_delay_days,
    ROUND(AVG(shipping_cost), 2) AS avg_shipping_cost
FROM orders
WHERE delivery_status = 'Delivered'
GROUP BY carrier
ORDER BY late_rate_pct DESC;


-- Query 3: Delivery performance by fulfillment center
SELECT
    fulfillment_center,
    COUNT(*) AS delivered_orders,
    SUM(late_delivery) AS late_orders,
    ROUND(100.0 * AVG(late_delivery), 2) AS late_rate_pct,
    ROUND(AVG(delay_days), 2) AS avg_delay_days
FROM orders
WHERE delivery_status = 'Delivered'
GROUP BY fulfillment_center
ORDER BY late_rate_pct DESC;


-- Query 4: Identify higher-risk operational segments
SELECT
    carrier,
    fulfillment_center,
    shipping_mode,
    COUNT(*) AS delivered_orders,
    SUM(late_delivery) AS late_orders,
    ROUND(100.0 * AVG(late_delivery), 2) AS late_rate_pct,
    ROUND(AVG(delay_days), 2) AS avg_delay_days,
    ROUND(AVG(shipping_cost), 2) AS avg_shipping_cost
FROM orders
WHERE delivery_status = 'Delivered'
GROUP BY carrier, fulfillment_center, shipping_mode
HAVING COUNT(*) >= 30
ORDER BY late_rate_pct DESC, delivered_orders DESC
LIMIT 20;
