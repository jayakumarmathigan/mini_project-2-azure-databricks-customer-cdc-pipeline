"""Typing and data quality rules, kept separate so they can be unit tested."""
from pyspark.sql import DataFrame
from pyspark.sql import functions as F

# Each rule is a SQL expression that is TRUE or FALSE, never NULL
RULES = {
    "valid_customer_id": "customer_id IS NOT NULL AND customer_id != ''",
    "valid_operation": "coalesce(operation IN ('INSERT', 'UPDATE', 'DELETE'), false)",
    "valid_sequence": "sequence_num IS NOT NULL",
    # DELETE events carry only the key, so the email rule does not apply to them
    "valid_email": ("coalesce(operation = 'DELETE', false) OR "
                    "coalesce(email LIKE '%_@_%._%', false)"),
}

VALID_CONDITION = " AND ".join(f"({rule})" for rule in RULES.values())


def cast_events(df: DataFrame) -> DataFrame:
    """Standardise raw string columns. Unparseable values become NULL."""
    return df.select(
        F.upper(F.trim("operation")).alias("operation"),
        F.trim("customer_id").alias("customer_id"),
        F.trim("name").alias("name"),
        F.lower(F.trim("email")).alias("email"),
        F.initcap(F.trim("city")).alias("city"),
        F.upper(F.trim("tier")).alias("tier"),
        F.expr("try_cast(sequence_num AS BIGINT)").alias("sequence_num"),
        F.expr("try_cast(event_time AS TIMESTAMP)").alias("event_time"),
    )


def with_failed_rules(df: DataFrame) -> DataFrame:
    """Add failed_rules: a comma-separated list of the rules each row breaks."""
    failures = [F.when(~F.expr(rule), F.lit(name)) for name, rule in RULES.items()]
    return df.withColumn("failed_rules", F.concat_ws(",", *failures))
