# =====================================================
# PURPLLE STORE INTELLIGENCE
# FASTAPI BACKEND
# =====================================================

import json

from fastapi import FastAPI, Request

from database import conn, cursor

# =====================================================
# CREATE FASTAPI APP
# =====================================================

app = FastAPI()

# =====================================================
# IN-MEMORY EVENT STORE
# =====================================================

all_events = []

# =====================================================
# LOAD EXISTING EVENTS FROM SQLITE
# =====================================================

def load_existing_events():

    cursor.execute("""

    SELECT
        event_id,
        store_id,
        camera_id,
        visitor_id,
        event_type,
        timestamp,
        zone_id,
        dwell_ms,
        is_staff,
        confidence,
        metadata

    FROM events

    """)

    rows = cursor.fetchall()

    for row in rows:

        metadata = {}

        try:

            metadata = json.loads(
                row[10]
            ) if row[10] else {}

        except:

            metadata = {}

        event = {

            "event_id": row[0],

            "store_id": row[1],

            "camera_id": row[2],

            "visitor_id": row[3],

            "event_type": row[4],

            "timestamp": row[5],

            "zone_id": row[6],

            "dwell_ms": row[7],

            "is_staff": row[8],

            "confidence": row[9],

            "metadata": metadata
        }

        all_events.append(event)

    print(
        f"Loaded {len(all_events)} events from SQLite"
    )

# =====================================================
# LOAD EVENTS ON STARTUP
# =====================================================

load_existing_events()

# =====================================================
# ROOT API
# =====================================================

@app.get("/")
def root():

    return {

        "message":
        "Purplle Store Intelligence Backend Running"
    }

# =====================================================
# HEALTH CHECK API
# =====================================================

@app.get("/health")
def health():

    latest_event_time = None

    latest_event_type = None

    if all_events:

        latest_event = all_events[-1]

        latest_event_time = latest_event.get(
            "timestamp"
        )

        latest_event_type = latest_event.get(
            "event_type"
        )

    return {

        "status": "healthy",

        "total_events": len(all_events),

        "latest_event_timestamp":
        latest_event_time,

        "latest_event_type":
        latest_event_type
    }

# =====================================================
# INGEST EVENTS API
# =====================================================

@app.post("/events/ingest")
async def ingest_event(request: Request):

    event = await request.json()

    existing_ids = {

        e["event_id"]

        for e in all_events
    }

    if event.get("event_id") in existing_ids:

        return {

            "status": "duplicate_event",

            "event_id": event.get("event_id")
        }

    # =================================================
    # STORE IN MEMORY
    # =================================================

    all_events.append(event)

    # =================================================
    # STORE IN SQLITE
    # =================================================

    cursor.execute("""

    INSERT INTO events (

        event_id,
        store_id,
        camera_id,
        visitor_id,
        event_type,
        timestamp,
        zone_id,
        dwell_ms,
        is_staff,
        confidence,
        metadata

    )

    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

    """, (

        event.get("event_id"),

        event.get("store_id"),

        event.get("camera_id"),

        event.get("visitor_id"),

        event.get("event_type"),

        event.get("timestamp"),

        event.get("zone_id"),

        event.get("dwell_ms"),

        event.get("is_staff"),

        event.get("confidence"),

        json.dumps(
            event.get("metadata", {})
        )

    ))

    conn.commit()

    print("\nReceived Event")

    print(event)

    return {

        "status": "success",

        "total_events": len(all_events)
    }

# =====================================================
# BATCH INGEST API
# =====================================================

@app.post("/events/batch_ingest")
async def batch_ingest(request: Request):

    payload = await request.json()

    batch_events = payload.get(
        "events",
        []
    )

    inserted = 0

    existing_ids = {

        e["event_id"]

        for e in all_events
    }

    for event in batch_events:

        # =============================================
        # SKIP DUPLICATES
        # =============================================

        if event.get("event_id") in existing_ids:

            continue

        # =============================================
        # STORE IN MEMORY
        # =============================================

        all_events.append(event)

        # =============================================
        # STORE IN SQLITE
        # =============================================

        cursor.execute("""

        INSERT INTO events (

            event_id,
            store_id,
            camera_id,
            visitor_id,
            event_type,
            timestamp,
            zone_id,
            dwell_ms,
            is_staff,
            confidence,
            metadata

        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

        """, (

            event.get("event_id"),

            event.get("store_id"),

            event.get("camera_id"),

            event.get("visitor_id"),

            event.get("event_type"),

            event.get("timestamp"),

            event.get("zone_id"),

            event.get("dwell_ms"),

            event.get("is_staff"),

            event.get("confidence"),

            json.dumps(
                event.get("metadata", {})
            )

        ))

        inserted += 1

    conn.commit()

    return {

        "status": "success",

        "inserted_events": inserted,

        "total_events": len(all_events)
    }

# =====================================================
# METRICS API
# =====================================================

@app.get("/metrics")
def get_metrics():

    zone_enter_count = 0

    zone_exit_count = 0

    queue_join_count = 0

    queue_exit_count = 0

    purchase_count = 0

    entry_count = 0

    exit_count = 0

    dwell_count = 0

    reentry_count = 0

    total_revenue = 0

    cameras = {}

    stores = {}

    zones = {}

    unique_visitors = set()

    for event in all_events:

        event_type = event.get("event_type")

        zone = event.get("zone_id")

        metadata = event.get("metadata", {})

        visitor_id = event.get("visitor_id")

        if visitor_id:

            unique_visitors.add(visitor_id)

        if event_type == "ZONE_ENTER":

            zone_enter_count += 1

        elif event_type == "ZONE_EXIT":

            zone_exit_count += 1

        elif event_type == "BILLING_QUEUE_JOIN":

            queue_join_count += 1

        elif event_type == "BILLING_QUEUE_EXIT":

            queue_exit_count += 1

        elif event_type == "PURCHASE":

            purchase_count += 1

            total_revenue += metadata.get(
                "basket_value_inr",
                0
            )

        elif event_type == "ENTRY":

            entry_count += 1

        elif event_type == "EXIT":

            exit_count += 1

        elif event_type == "ZONE_DWELL":

            dwell_count += 1

        elif event_type == "REENTRY":

            reentry_count += 1

        # =============================================
        # CAMERA DISTRIBUTION
        # =============================================

        cam = event.get(
            "camera_id",
            "UNKNOWN"
        )

        cameras[cam] = (

            cameras.get(cam, 0)
            + 1
        )

        # =============================================
        # STORE DISTRIBUTION
        # =============================================

        store = event.get(
            "store_id",
            "UNKNOWN"
        )

        stores[store] = (

            stores.get(store, 0)
            + 1
        )

        # =============================================
        # ZONE ACTIVITY
        # =============================================

        if zone:

            zones[zone] = (

                zones.get(zone, 0)
                + 1
            )

    # =================================================
    # CONVERSION RATE
    # =================================================

    total_visitors = len(unique_visitors)

    conversion_rate = 0

    if total_visitors > 0:

        conversion_rate = round(

            (
                purchase_count
                /
                total_visitors
            ) * 100,

            2
        )

    # =================================================
    # TOP ACTIVE ZONE
    # =================================================

    top_zone = None

    if zones:

        top_zone = max(

            zones,

            key=zones.get
        )

    return {

        "total_events": len(all_events),

        "total_visitors": total_visitors,

        "entry_events": entry_count,

        "exit_events": exit_count,

        "zone_enter_events": zone_enter_count,

        "zone_exit_events": zone_exit_count,

        "queue_join_events": queue_join_count,

        "queue_exit_events": queue_exit_count,

        "purchase_events": purchase_count,

        "zone_dwell_events": dwell_count,

        "reentry_events": reentry_count,

        "conversion_rate": conversion_rate,

        "total_revenue_inr": round(
            total_revenue,
            2
        ),

        "top_active_zone": top_zone,

        "camera_distribution": cameras,

        "store_distribution": stores
    }

# =====================================================
# HEATMAP API
# =====================================================

@app.get("/heatmap")
def heatmap():

    zones = {}

    for event in all_events:

        zone = event.get("zone_id")

        if zone:

            zones[zone] = (

                zones.get(zone, 0)
                + 1
            )

    return {

        "zone_activity": zones
    }

# =====================================================
# ANOMALY DETECTION API
# =====================================================

@app.get("/anomalies")
def anomalies():

    anomalies_detected = []

    queue_events = 0

    purchase_events = 0

    for event in all_events:

        if event.get("event_type") == "BILLING_QUEUE_JOIN":

            queue_events += 1

        elif event.get("event_type") == "PURCHASE":

            purchase_events += 1

    if queue_events > 10:

        anomalies_detected.append(

            "High billing queue activity detected"
        )

    if (

        queue_events > 0

        and

        purchase_events == 0
    ):

        anomalies_detected.append(

            "Low billing conversion detected"
        )

    return {

        "anomalies": anomalies_detected
    }

# =====================================================
# STORE METRICS API
# =====================================================

@app.get("/stores/{store_id}/metrics")
def store_metrics(store_id: str):

    store_events = [

        e for e in all_events

        if e.get("store_id") == store_id
    ]

    return {

        "store_id": store_id,

        "total_events": len(store_events),

        "events": store_events[:20]
    }

# =====================================================
# STORE FUNNEL API
# =====================================================

@app.get("/stores/{store_id}/funnel")
def store_funnel(store_id: str):

    store_events = [

        e for e in all_events

        if e.get("store_id") == store_id
    ]

    visitors = {}

    for event in store_events:

        visitor_id = event.get(
            "visitor_id"
        )

        event_type = event.get(
            "event_type"
        )

        if not visitor_id:

            continue

        if visitor_id not in visitors:

            visitors[visitor_id] = {

                "entered": False,

                "engaged": False,

                "queued": False,

                "purchased": False
            }

        if event_type == "ENTRY":

            visitors[visitor_id][
                "entered"
            ] = True

        elif event_type == "ZONE_DWELL":

            visitors[visitor_id][
                "engaged"
            ] = True

        elif event_type == "BILLING_QUEUE_JOIN":

            visitors[visitor_id][
                "queued"
            ] = True

        elif event_type == "PURCHASE":

            visitors[visitor_id][
                "purchased"
            ] = True

    entered = 0

    engaged = 0

    queued = 0

    purchased = 0

    for visitor in visitors.values():

        if visitor["entered"]:

            entered += 1

        if visitor["engaged"]:

            engaged += 1

        if visitor["queued"]:

            queued += 1

        if visitor["purchased"]:

            purchased += 1

    engagement_rate = 0

    queue_rate = 0

    purchase_rate = 0

    if entered > 0:

        engagement_rate = round(
            (engaged / entered) * 100,
            2
        )

        queue_rate = round(
            (queued / entered) * 100,
            2
        )

        purchase_rate = round(
            (purchased / entered) * 100,
            2
        )

    return {

        "store_id": store_id,

        "funnel": {

            "entered": entered,

            "engaged": engaged,

            "billing_queue": queued,

            "purchased": purchased
        },

        "conversion_rates": {

            "engagement_rate":
            engagement_rate,

            "queue_rate":
            queue_rate,

            "purchase_rate":
            purchase_rate
        }
    }

# =====================================================
# GET ALL EVENTS
# =====================================================

@app.get("/events")
def get_all_events():

    return {

        "total_events": len(all_events),

        "events": all_events
    }

