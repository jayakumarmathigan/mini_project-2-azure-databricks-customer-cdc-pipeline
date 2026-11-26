from utilities.rules import VALID_CONDITION, cast_events, with_failed_rules

COLS = ["operation", "customer_id", "name", "email", "city", "tier",
        "sequence_num", "event_time"]


def typed(spark, **changes):
    row = dict(zip(COLS, ["insert", "C001", "Asha", "Asha@Example.com", "pune",
                          "gold", "1", "2026-10-01 09:01:00"]))
    row.update(changes)
    df = spark.createDataFrame([tuple(row[c] for c in COLS)],
                               ", ".join(f"{c} string" for c in COLS))
    return cast_events(df)


def failed(spark, **changes):
    return with_failed_rules(typed(spark, **changes)).first()["failed_rules"]


def test_values_are_standardised(spark):
    row = typed(spark).first()
    assert row["operation"] == "INSERT"
    assert row["email"] == "asha@example.com"
    assert row["city"] == "Pune"
    assert row["sequence_num"] == 1


def test_valid_event_passes(spark):
    assert typed(spark).filter(VALID_CONDITION).count() == 1
    assert failed(spark) == ""


def test_delete_without_email_is_valid(spark):
    assert failed(spark, operation="DELETE", email=None) == ""


def test_invalid_events_are_flagged(spark):
    cases = [
        ({"customer_id": None}, "valid_customer_id"),
        ({"operation": "UPSERT"}, "valid_operation"),
        ({"operation": None}, "valid_operation"),
        ({"sequence_num": "abc"}, "valid_sequence"),
        ({"email": "not-an-email"}, "valid_email"),
        ({"email": None}, "valid_email"),
    ]
    for changes, rule in cases:
        assert failed(spark, **changes) == rule, changes
        assert typed(spark, **changes).filter(VALID_CONDITION).count() == 0
