-- =====================================================================
-- DeliverIQ: Supply Chain Delivery Performance & Shipping Optimization
-- SQL Analytics Layer
-- Database: SQLite / ANSI SQL Compatible
-- =====================================================================

-- ---------------------------------------------------------------------
-- 1. Executive Summary: Delivery Performance Breakdown & Percentages
-- Business Question: What is the distribution and share of delivery outcomes?
-- ---------------------------------------------------------------------
SELECT 
    delivery_performance,
    COUNT(*) AS order_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM orders), 2) AS percentage
FROM orders
GROUP BY delivery_performance
ORDER BY order_count DESC;


-- ---------------------------------------------------------------------
-- 2. Shipping Mode Efficiency: The "Expedited Shipping" Analysis
-- Business Question: Are premium shipping modes fulfilling their promises?
-- ---------------------------------------------------------------------
SELECT 
    shipping_mode,
    COUNT(*) AS total_orders,
    ROUND(AVG(days_for_shipment_scheduled), 2) AS avg_scheduled_days,
    ROUND(AVG(days_for_shipping_real), 2) AS avg_actual_days,
    ROUND(AVG(shipping_delay_days), 2) AS avg_delay_days,
    ROUND(SUM(CASE WHEN shipping_delay_days > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS late_rate_pct
FROM orders
GROUP BY shipping_mode
ORDER BY late_rate_pct DESC;


-- ---------------------------------------------------------------------
-- 3. High-Volume Regional Risk Analysis (HAVING Clause)
-- Business Question: Which high-volume regions have the highest delay risks?
-- ---------------------------------------------------------------------
SELECT 
    order_region,
    market,
    COUNT(*) AS total_orders,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(AVG(shipping_delay_days), 2) AS avg_delay_days,
    ROUND(AVG(late_delivery_risk) * 100.0, 2) AS late_risk_pct
FROM orders
GROUP BY order_region, market
HAVING COUNT(*) > 5000
ORDER BY late_risk_pct DESC;


-- ---------------------------------------------------------------------
-- 4. Top 3 Worst Delayed Product Categories per Market (CTEs & Window Functions)
-- Business Question: Which product categories in each global market suffer the worst delays?
-- ---------------------------------------------------------------------
WITH category_delays AS (
    SELECT 
        market,
        category_name,
        COUNT(*) AS total_orders,
        ROUND(AVG(shipping_delay_days), 2) AS avg_delay_days,
        ROUND(AVG(late_delivery_risk) * 100.0, 2) AS late_risk_pct,
        ROW_NUMBER() OVER (
            PARTITION BY market 
            ORDER BY AVG(late_delivery_risk) DESC
        ) AS rank_in_market
    FROM orders
    GROUP BY market, category_name
    HAVING COUNT(*) >= 100
)
SELECT 
    market,
    category_name,
    total_orders,
    avg_delay_days,
    late_risk_pct,
    rank_in_market
FROM category_delays
WHERE rank_in_market <= 3;
