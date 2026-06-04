# =====================================================
# UNIFIED PURCHASE CORRELATION ENGINE
# =====================================================

import json
import uuid
import pandas as pd

# =====================================================
# PATHS
# =====================================================

EVENTS_PATH = "../data/unified/all_events.jsonl"

POS_PATH = "../data/unified/pos_transactions.csv"

# =====================================================
# LOAD EVENTS
# =====================================================

events = []

with open(EVENTS_PATH, "r") as f:

    for line in f:

        events.append(
            json.loads(line)
        )

print(f"\nLoaded {len(events)} events")

# =====================================================
# LOAD POS DATA
# =====================================================

pos_df = pd.read_csv(POS_PATH)

print("\nPOS Data Loaded")

print(pos_df.head())

# =====================================================
# CREATE POS TIMESTAMP
# =====================================================

pos_df["timestamp"] = pd.to_datetime(

    pos_df["order_date"]
    +
    " "
    +
    pos_df["order_time"],

    format="%d-%m-%Y %H:%M:%S"
)

# =====================================================
# FIND BILLING EVENTS
# =====================================================

billing_events = [

    e for e in events

    if e["event_type"] == "BILLING_QUEUE_JOIN"
]

print(
    f"\nFound {len(billing_events)} billing events"
)

# =====================================================
# TRACK USED VISITORS
# =====================================================

used_visitors = set()

# =====================================================
# PURCHASE EVENTS
# =====================================================

purchase_events = []

# =====================================================
# CORRELATE PURCHASES
# =====================================================

for _, txn in pos_df.iterrows():

    txn_time = txn["timestamp"]

    matched_event = None

    smallest_time_diff = None

    # =============================================
    # FIND BEST BILLING MATCH
    # =============================================

    for event in billing_events:

        visitor_id = event["visitor_id"]

        # =========================================
        # PREVENT REUSE
        # =========================================

        if visitor_id in used_visitors:

            continue

        event_time = pd.to_datetime(
            event["timestamp"]
        )

        time_diff = abs(
            (txn_time - event_time)
            .total_seconds()
        )

        # =========================================
        # RELAXED MATCHING
        # FOR SYNTHETIC DATA
        # =========================================

        if (

            smallest_time_diff is None

            or

            time_diff < smallest_time_diff
        ):

            matched_event = event

            smallest_time_diff = time_diff

    # =============================================
    # CREATE PURCHASE EVENT
    # =============================================

    if matched_event:

        visitor_id = matched_event[
            "visitor_id"
        ]

        used_visitors.add(
            visitor_id
        )

        purchase_event = {

            "event_id": str(uuid.uuid4()),

            "store_id": matched_event[
                "store_id"
            ],

            "camera_id": "POS_SYSTEM",

            "visitor_id": visitor_id,

            "event_type": "PURCHASE",

            "timestamp": txn_time.isoformat(),

            "zone_id": "BILLING",

            "dwell_ms": None,

            "is_staff": False,

            "confidence": 0.95,

            "metadata": {

                "transaction_id":
                int(txn["order_id"]),

                "product_id":
                int(txn["product_id"]),

                "brand_name":
                txn["brand_name"],

                "basket_value_inr":
                float(txn["total_amount"])
            }
        }

        purchase_events.append(
            purchase_event
        )

# =====================================================
# APPEND PURCHASE EVENTS
# =====================================================

events.extend(purchase_events)

# =====================================================
# SORT EVENTS
# =====================================================

events.sort(
    key=lambda x: x["timestamp"]
)

# =====================================================
# SAVE UPDATED EVENTS
# =====================================================

with open(EVENTS_PATH, "w") as f:

    for event in events:

        f.write(
            json.dumps(event)
            + "\n"
        )

print(
    f"\nAdded {len(purchase_events)} PURCHASE events"
)

print(
    "\nUpdated unified all_events.jsonl"
)

