-- Change the next line if you used a different catalog or schema.
USE workspace.customer_cdc;

-- 1. Full history of one customer who moved twice
SELECT customer_id, city, tier, __START_AT, __END_AT
FROM silver_customers_history
WHERE customer_id = 'C001'
ORDER BY __START_AT;

-- 2. Deleted customers (no open version left)
SELECT customer_id, version_count
FROM gold_customer_change_summary
WHERE NOT is_active
ORDER BY customer_id;

-- 3. Customers with the most versions
SELECT customer_id, version_count
FROM gold_customer_change_summary
ORDER BY version_count DESC, customer_id
LIMIT 10;

-- 4. Active customers by city
SELECT city, SUM(active_customers) AS customers
FROM gold_customers_by_city
GROUP BY city
ORDER BY customers DESC;

-- 5. Rejected events by failed rule
SELECT failed_rules, COUNT(*) AS events
FROM quarantine_customer_cdc
GROUP BY failed_rules
ORDER BY events DESC;
