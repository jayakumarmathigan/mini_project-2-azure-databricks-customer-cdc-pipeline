# Databricks notebook source
# MAGIC %md
# MAGIC # Validate results
# MAGIC Run after a pipeline update. Raises an error if any check fails.

# COMMAND ----------

dbutils.widgets.text("catalog", "workspace")
dbutils.widgets.text("schema", "customer_cdc")
p = f"{dbutils.widgets.get('catalog')}.{dbutils.widgets.get('schema')}"

current = f"{p}.silver_customers_current"
history = f"{p}.silver_customers_history"
open_keys = f"SELECT customer_id FROM {history} WHERE __END_AT IS NULL"

# COMMAND ----------

# Each query returns the number of violations (0 = pass)
checks = {
    "current table has rows":
        f"SELECT CASE WHEN COUNT(*) = 0 THEN 1 ELSE 0 END FROM {current}",
    "one current row per customer":
        f"SELECT COUNT(*) FROM (SELECT customer_id FROM {current} "
        "GROUP BY customer_id HAVING COUNT(*) > 1)",
    "at most one open history version per customer":
        f"SELECT COUNT(*) FROM ({open_keys} GROUP BY customer_id HAVING COUNT(*) > 1)",
    "every current customer has an open version":
        f"SELECT COUNT(*) FROM (SELECT customer_id FROM {current} EXCEPT {open_keys})",
    "every open version is a current customer":
        f"SELECT COUNT(*) FROM ({open_keys} EXCEPT SELECT customer_id FROM {current})",
    "history ranges are ordered":
        f"SELECT COUNT(*) FROM {history} WHERE __END_AT <= __START_AT",
}

failed = []
for name, query in checks.items():
    violations = spark.sql(query).first()[0]
    print(f"{'PASS' if violations == 0 else 'FAIL'} | {name} | violations={violations}")
    if violations:
        failed.append(name)

# COMMAND ----------

for table in ["bronze_customer_cdc", "quarantine_customer_cdc",
              "silver_customers_current", "silver_customers_history"]:
    print(table, spark.table(f"{p}.{table}").count())

if failed:
    raise ValueError(f"Checks failed: {failed}")
