"""Generate synthetic customer change events (CDC) as JSON Lines files.

Usage:  python data/generate_data.py
The fixed random seed means every run produces the same files.
"""
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(7)
OUT = Path(__file__).parent / "sample"
CITIES = ["Bengaluru", "Hyderabad", "Chennai", "Pune", "Mumbai", "Delhi"]
TIERS = ["BRONZE", "SILVER", "GOLD"]
START = datetime(2026, 10, 1, 9, 0, 0)


def event_time(sequence):
    minutes = sequence if isinstance(sequence, int) else 0
    return (START + timedelta(minutes=minutes)).strftime("%Y-%m-%d %H:%M:%S")


def event(operation, customer_id, sequence, profile=None):
    profile = profile or {}
    return {
        "operation": operation,
        "customer_id": customer_id,
        "name": profile.get("name"),
        "email": profile.get("email"),
        "city": profile.get("city"),
        "tier": profile.get("tier"),
        "sequence_num": sequence,
        "event_time": event_time(sequence),
    }


def profile_for(number):
    return {"name": f"Customer {number}", "email": f"customer{number}@example.com",
            "city": random.choice(CITIES), "tier": random.choice(TIERS)}


def write(name, events):
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / name, "w", encoding="utf-8") as f:
        f.writelines(json.dumps(e) + "\n" for e in events)
    print(f"{name}: {len(events)} events")


def main():
    profiles = {f"C{i:03d}": profile_for(i) for i in range(1, 101)}

    # Batch 1: 100 inserts + 4 invalid events
    batch1 = [event("INSERT", key, n, value)
              for n, (key, value) in enumerate(profiles.items(), start=1)]
    sample = profile_for(900)
    bad_email = {**sample, "email": "not-an-email"}
    batch1 += [
        event("INSERT", None, 901, sample),          # missing key
        event("UPSERT", "C901", 902, sample),        # unknown operation
        event("INSERT", "C902", "abc", sample),      # bad sequence number
        event("INSERT", "C903", 903, bad_email),     # bad email
    ]
    random.shuffle(batch1)

    # Batch 2: 35 updates, 10 deletes, 15 inserts and 3 invalid events
    batch2, sequence = [], 1000

    def change_city(key):
        current = profiles[key]["city"]
        profiles[key] = {**profiles[key],
                         "city": random.choice([c for c in CITIES if c != current])}

    # C001-C030 move once; C001-C005 then move a second time
    for number in list(range(1, 31)) + list(range(1, 6)):
        key = f"C{number:03d}"
        change_city(key)
        sequence += 1
        batch2.append(event("UPDATE", key, sequence, profiles[key]))
    for number in range(91, 101):
        sequence += 1
        batch2.append(event("DELETE", f"C{number:03d}", sequence))
    for number in range(101, 116):
        sequence += 1
        batch2.append(event("INSERT", f"C{number:03d}", sequence, profile_for(number)))
    batch2 += [
        event("UPDATE", None, 2001, sample),
        event("MERGE", "C001", 2002, sample),
        event("UPDATE", "C002", 2003, bad_email),
    ]
    random.shuffle(batch2)  # events arrive out of order on purpose

    write("customers_cdc_batch_1.json", batch1)
    write("customers_cdc_batch_2.json", batch2)


if __name__ == "__main__":
    main()
