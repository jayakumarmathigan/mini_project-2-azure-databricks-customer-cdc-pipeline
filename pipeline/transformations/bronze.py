"""Bronze: raw change events, ingested incrementally with Auto Loader."""
from pyspark import pipelines as dp
from pyspark.sql import functions as F

landing_path = spark.conf.get("landing_path")  # set in the pipeline configuration

SCHEMA = ", ".join(f"{name} STRING" for name in [
    "operation", "customer_id", "name", "email", "city", "tier",
    "sequence_num", "event_time"])


@dp.table(name="bronze_customer_cdc", comment="Raw customer change events")
def bronze_customer_cdc():
    return (spark.readStream.format("cloudFiles")
            .option("cloudFiles.format", "json")
            .schema(SCHEMA)
            .load(landing_path)
            .select("*",
                    F.col("_metadata.file_path").alias("_source_file"),
                    F.current_timestamp().alias("_ingested_at")))
