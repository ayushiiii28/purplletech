# =====================================================# EVENT REPLAY ENGINE
# =====================================================

import json
import time
import requests

from datetime import datetime

# =====================================================
# CONFIG
# =====================================================

EVENTS_FILE = "/app/data/unified/all_events.jsonl"

BACKEND_URL = (
    "http://backend:8000/events/batch_ingest"
)

BATCH_SIZE = 5

REPLAY_DELAY = 1.0

# =====================================================
# LOAD EVENTS
# =====================================================

events = []

with open(EVENTS_FILE, "r") as f:

    for line in f:

        event = json.loads(line)

        events.append(event)

print(f"\nLoaded {len(events)} events")

# =====================================================
# SORT EVENTS
# =====================================================

events.sort(
    key=lambda x: datetime.fromisoformat(
        x["timestamp"]
    )
)

# =====================================================
# CREATE BATCHES
# =====================================================

batches = [

    events[i:i+BATCH_SIZE]

    for i in range(
        0,
        len(events),
        BATCH_SIZE
    )
]

print(
    f"\nCreated {len(batches)} batches"
)

# =====================================================
# REPLAY BATCHES
# =====================================================

for batch_index, batch in enumerate(batches):

    print("\n" + "=" * 60)

    print(

        f"Sending Batch "
        f"{batch_index+1}/{len(batches)}"

    )

    print(
        f"Batch Size: {len(batch)}"
    )

    payload = {

        "events": batch
    }

    try:

        response = requests.post(

            BACKEND_URL,

            json=payload
        )

        print(
            f"Backend Response: "
            f"{response.status_code}"
        )

        print(
            response.json()
        )

    except Exception as e:

        print(f"ERROR: {e}")

    # =================================================
    # SIMULATE STREAMING
    # =================================================

    time.sleep(REPLAY_DELAY)

print("\nReplay Complete")

