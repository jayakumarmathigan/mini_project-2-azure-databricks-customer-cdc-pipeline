# Databricks notebook source
# MAGIC %md
# MAGIC # Setup
# MAGIC Creates the schema and volume, then copies one batch of change events to the landing folder.

# COMMAND ----------

import os
import shutil

dbutils.widgets.text("catalog", "workspace")
dbutils.widgets.text("schema", "customer_cdc")
dbutils.widgets.dropdown("batch", "1", ["1", "2"])

catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
batch = dbutils.widgets.get("batch")

# COMMAND ----------

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog}.{schema}")
spark.sql(f"CREATE VOLUME IF NOT EXISTS {catalog}.{schema}.files")

landing = f"/Volumes/{catalog}/{schema}/files/landing"
os.makedirs(landing, exist_ok=True)

file_name = f"customers_cdc_batch_{batch}.json"
target = f"{landing}/{file_name}"
if os.path.exists(target):
    print(f"Already present, skipped: {target}")
else:
    shutil.copyfile(os.path.abspath(f"../data/sample/{file_name}"), target)
    print(f"Copied: {target}")

print(f"Pipeline configuration -> landing_path = {landing}")
