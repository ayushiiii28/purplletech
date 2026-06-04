# =====================================================
# MERGE MULTI-STORE EVENT STREAMS
# =====================================================

import json

# =====================================================
# INPUT FILES
# =====================================================

store_1_file = "../data/store_001/events.jsonl"

store_2_file = "../data/store_002/events.jsonl"

# =====================================================
# OUTPUT FILE
# =====================================================

output_file = "../data/unified/all_events.jsonl"

# =====================================================
# LOAD EVENTS
# =====================================================

all_events = []

# =====================================================
# LOAD STORE 1
# =====================================================

with open(store_1_file, "r") as f:

    for line in f:

        all_events.append(
            json.loads(line)
        )

# =====================================================
# LOAD STORE 2
# =====================================================

with open(store_2_file, "r") as f:

    for line in f:

        all_events.append(
            json.loads(line)
        )

# =====================================================
# SORT BY TIMESTAMP
# =====================================================

all_events.sort(
    key=lambda x: x["timestamp"]
)

# =====================================================
# SAVE MERGED FILE
# =====================================================

with open(output_file, "w") as f:

    for event in all_events:

        f.write(
            json.dumps(event)
            + "\n"
        )

print(
    f"\nMerged {len(all_events)} events"
)

print(
    f"\nSaved to: {output_file}"
)

