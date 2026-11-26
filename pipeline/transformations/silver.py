"""Silver: validate events, quarantine bad ones and apply changes with AUTO CDC."""
from pyspark import pipelines as dp
from pyspark.sql import functions as F

from utilities.rules import RULES, VALID_CONDITION, cast_events, with_failed_rules


@dp.temporary_view(name="customer_cdc_clean")
@dp.expect_all_or_drop(RULES)  # drops bad rows and records quality metrics
def customer_cdc_clean():
    return cast_events(spark.readStream.table("bronze_customer_cdc"))


@dp.table(name="quarantine_customer_cdc", comment="Rejected events and why")
def quarantine_customer_cdc():
    typed = cast_events(spark.readStream.table("bronze_customer_cdc"))
    return with_failed_rules(typed.filter(f"NOT ({VALID_CONDITION})"))


# SCD Type 1: one row per active customer, latest values only
dp.create_streaming_table(name="silver_customers_current")

dp.create_auto_cdc_flow(
    target="silver_customers_current",
    source="customer_cdc_clean",
    keys=["customer_id"],
    sequence_by=F.col("sequence_num"),
    apply_as_deletes=F.expr("operation = 'DELETE'"),
    except_column_list=["operation", "sequence_num"],
    stored_as_scd_type=1,
)

# SCD Type 2: every version, with __START_AT and __END_AT
dp.create_streaming_table(name="silver_customers_history")

dp.create_auto_cdc_flow(
    target="silver_customers_history",
    source="customer_cdc_clean",
    keys=["customer_id"],
    sequence_by=F.col("sequence_num"),
    apply_as_deletes=F.expr("operation = 'DELETE'"),
    except_column_list=["operation", "sequence_num"],
    stored_as_scd_type=2,
)
