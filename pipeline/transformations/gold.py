"""Gold: reporting datasets."""
from pyspark import pipelines as dp
from pyspark.sql import functions as F


@dp.materialized_view(name="gold_customers_by_city")
def gold_customers_by_city():
    return (spark.read.table("silver_customers_current")
            .groupBy("city", "tier")
            .agg(F.count("*").alias("active_customers")))


@dp.materialized_view(name="gold_customer_change_summary")
def gold_customer_change_summary():
    return (spark.read.table("silver_customers_history")
            .groupBy("customer_id")
            .agg(F.count("*").alias("version_count"),
                 F.max(F.col("__END_AT").isNull().cast("int")).alias("is_active_flag"))
            .select("customer_id", "version_count",
                    (F.col("is_active_flag") == 1).alias("is_active")))
