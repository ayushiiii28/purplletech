# =====================================================
# PURPLLE GENERIC STORE PIPELINE
# =====================================================

import cv2
import json
import uuid
import argparse
import numpy as np
import supervision as sv

from ultralytics import YOLO
from datetime import datetime

# =====================================================
# ARGUMENT PARSER
# =====================================================

parser = argparse.ArgumentParser()

parser.add_argument(
    "--config",
    required=True,
    help="Store config JSON"
)

args = parser.parse_args()

# =====================================================
# LOAD CONFIG
# =====================================================

CONFIG_PATH = args.config

with open(CONFIG_PATH, "r") as f:

    config = json.load(f)

STORE_ID = config["store_id"]

# =====================================================
# OUTPUT PATH
# =====================================================

OUTPUT_PATH = (
    f"../data/{STORE_ID.lower()}/events.jsonl"
)

# =====================================================
# LOAD YOLO MODEL
# =====================================================

model = YOLO("yolov8n.pt")

# =====================================================
# GLOBAL EVENTS
# =====================================================

events = []

# =====================================================
# SETTINGS
# =====================================================

MIN_DWELL_MS = 2000

DWELL_EMIT_INTERVAL_MS = 30000

QUEUE_COOLDOWN_SEC = 5

REENTRY_WINDOW_SEC = 120

ZONE_STABILITY_SEC = 1.0

# =====================================================
# CREATE EVENT
# =====================================================

def create_event(
    visitor_id,
    camera_id,
    event_type,
    zone_id=None,
    dwell_ms=None,
    confidence=0.90,
    metadata=None
):

    event = {

        "event_id": str(uuid.uuid4()),

        "store_id": STORE_ID,

        "camera_id": camera_id,

        "visitor_id": visitor_id,

        "event_type": event_type,

        "timestamp": datetime.utcnow().isoformat(),

        "zone_id": zone_id,

        "dwell_ms": dwell_ms,

        "is_staff": False,

        "confidence": confidence,

        "metadata": metadata or {

            "pipeline_version": "v6",

            "session_seq": 1
        }
    }

    events.append(event)

    print(event)

# =====================================================
# POINT INSIDE POLYGON
# =====================================================

def point_in_zone(point, polygon):

    return cv2.pointPolygonTest(
        polygon,
        point,
        False
    ) >= 0

# =====================================================
# PROCESS CAMERAS
# =====================================================

for camera_id, camera_data in config["cameras"].items():

    print("\n" + "=" * 60)

    print(f"PROCESSING {camera_id}")

    print("=" * 60)

    video_path = camera_data["video_path"]

    purpose = camera_data["purpose"]

    zones = {

        zone_name: np.array(points)

        for zone_name, points

        in camera_data["zones"].items()
    }

    # =================================================
    # VIDEO + TRACKER
    # =================================================

    cap = cv2.VideoCapture(video_path)

    print(f"\nVideo Path: {video_path}")

    print(
        "Video Opened:",
        cap.isOpened()
    )

    tracker = sv.ByteTrack()

    # =================================================
    # TRACKING STATE
    # =================================================

    previous_zones = {}

    candidate_zones = {}

    candidate_zone_start = {}

    entry_times = {}

    last_dwell_emit = {}

    queue_entered = set()

    active_visitors = set()

    exited_visitors = {}

    last_queue_event_time = {}

    frame_count = 0

    # =================================================
    # PROCESS VIDEO
    # =================================================

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        # =============================================
        # YOLO DETECTION
        # =============================================

        results = model(frame, verbose=False)

        detections = sv.Detections.from_ultralytics(
            results[0]
        )

        tracked = tracker.update_with_detections(
            detections
        )

        # =============================================
        # DRAW ZONES
        # =============================================

        for zone_name, polygon in zones.items():

            cv2.polylines(

                frame,

                [polygon],

                True,

                (0,255,0),

                2
            )

            x, y = polygon[0]

            cv2.putText(

                frame,

                zone_name,

                (x, y-10),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.7,

                (255,0,0),

                2
            )

        # =============================================
        # TRACK PERSONS
        # =============================================

        for i in range(len(tracked.xyxy)):

            x1, y1, x2, y2 = tracked.xyxy[i].astype(int)

            tracker_id = int(
                tracked.tracker_id[i]
            )

            cls_id = int(
                tracked.class_id[i]
            )

            # =========================================
            # PERSON ONLY
            # =========================================

            if cls_id != 0:
                continue

            visitor_id = f"VIS_{tracker_id}"

            # =========================================
            # CENTROID
            # =========================================

            cx = int((x1 + x2) / 2)

            cy = int((y1 + y2) / 2)

            # =========================================
            # DRAW PERSON
            # =========================================

            cv2.rectangle(

                frame,

                (x1,y1),

                (x2,y2),

                (0,255,0),

                2
            )

            cv2.putText(

                frame,

                visitor_id,

                (x1, y1-10),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.7,

                (0,255,0),

                2
            )

            cv2.circle(

                frame,

                (cx,cy),

                5,

                (255,0,0),

                -1
            )

            # =========================================
            # FIND RAW ZONE
            # =========================================

            raw_zone = None

            for zone_name, polygon in zones.items():

                if point_in_zone(
                    (cx, cy),
                    polygon
                ):

                    raw_zone = zone_name

                    break

            current_time = datetime.utcnow()

            # =========================================
            # STABLE ZONE TRACKING
            # =========================================

            previous_zone = previous_zones.get(
                tracker_id
            )

            current_zone = previous_zone

            candidate_zone = candidate_zones.get(
                tracker_id
            )

            candidate_start = candidate_zone_start.get(
                tracker_id
            )

            # =========================================
            # NEW CANDIDATE ZONE
            # =========================================

            if raw_zone != candidate_zone:

                candidate_zones[
                    tracker_id
                ] = raw_zone

                candidate_zone_start[
                    tracker_id
                ] = current_time

            # =========================================
            # CONFIRM STABLE ZONE
            # =========================================

            else:

                if candidate_start:

                    stable_duration = (

                        current_time
                        -
                        candidate_start

                    ).total_seconds()

                    if stable_duration >= ZONE_STABILITY_SEC:

                        current_zone = raw_zone

            # =========================================
            # ENTRY / REENTRY
            # =========================================

            if purpose == "entry_tracking":

                if (

                    current_zone == "ENTRY_GATE"

                    and tracker_id not in active_visitors
                ):

                    # =================================
                    # REENTRY
                    # =================================

                    if tracker_id in exited_visitors:

                        last_exit = exited_visitors[
                            tracker_id
                        ]

                        diff = (

                            current_time - last_exit

                        ).total_seconds()

                        if diff <= REENTRY_WINDOW_SEC:

                            create_event(

                                visitor_id=visitor_id,

                                camera_id=camera_id,

                                event_type="REENTRY",

                                zone_id="ENTRY_GATE"
                            )

                    # =================================
                    # ENTRY
                    # =================================

                    create_event(

                        visitor_id=visitor_id,

                        camera_id=camera_id,

                        event_type="ENTRY",

                        zone_id="ENTRY_GATE"
                    )

                    active_visitors.add(
                        tracker_id
                    )

                # =====================================
                # EXIT
                # =====================================

                elif (

                    tracker_id in active_visitors

                    and current_zone != "ENTRY_GATE"
                ):

                    create_event(

                        visitor_id=visitor_id,

                        camera_id=camera_id,

                        event_type="EXIT",

                        zone_id="EXIT_GATE"
                    )

                    active_visitors.remove(
                        tracker_id
                    )

                    exited_visitors[
                        tracker_id
                    ] = current_time

            # =========================================
            # ZONE ENTER
            # =========================================

            if (

                current_zone

                and current_zone != previous_zone
            ):

                create_event(

                    visitor_id=visitor_id,

                    camera_id=camera_id,

                    event_type="ZONE_ENTER",

                    zone_id=current_zone
                )

                entry_times[
                    (tracker_id, current_zone)
                ] = current_time

            # =========================================
            # ZONE DWELL
            # =========================================

            if current_zone:

                zone_key = (
                    tracker_id,
                    current_zone
                )

                if zone_key in entry_times:

                    dwell_ms = int(

                        (
                            current_time
                            -
                            entry_times[zone_key]
                        ).total_seconds() * 1000
                    )

                    last_emit = last_dwell_emit.get(
                        zone_key,
                        0
                    )

                    if (

                        dwell_ms >= MIN_DWELL_MS

                        and

                        dwell_ms - last_emit
                        >= DWELL_EMIT_INTERVAL_MS
                    ):

                        create_event(

                            visitor_id=visitor_id,

                            camera_id=camera_id,

                            event_type="ZONE_DWELL",

                            zone_id=current_zone,

                            dwell_ms=dwell_ms
                        )

                        last_dwell_emit[
                            zone_key
                        ] = dwell_ms

            # =========================================
            # ZONE EXIT
            # =========================================

            if (

                previous_zone

                and current_zone != previous_zone
            ):

                zone_key = (
                    tracker_id,
                    previous_zone
                )

                dwell_ms = None

                if zone_key in entry_times:

                    dwell_ms = int(

                        (
                            current_time
                            -
                            entry_times[zone_key]
                        ).total_seconds() * 1000
                    )

                create_event(

                    visitor_id=visitor_id,

                    camera_id=camera_id,

                    event_type="ZONE_EXIT",

                    zone_id=previous_zone,

                    dwell_ms=dwell_ms
                )

            # =========================================
            # BILLING QUEUE EVENTS
            # =========================================

            if purpose == "billing_queue":

                last_time = last_queue_event_time.get(
                    tracker_id
                )

                cooldown_passed = True

                if last_time:

                    diff = (
                        current_time - last_time
                    ).total_seconds()

                    if diff < QUEUE_COOLDOWN_SEC:

                        cooldown_passed = False

                # =====================================
                # BILLING_QUEUE_JOIN
                # =====================================

                if (

                    current_zone == "BILLING_QUEUE"

                    and tracker_id not in queue_entered

                    and cooldown_passed
                ):

                    create_event(

                        visitor_id=visitor_id,

                        camera_id=camera_id,

                        event_type="BILLING_QUEUE_JOIN",

                        zone_id="BILLING_QUEUE"
                    )

                    queue_entered.add(
                        tracker_id
                    )

                    last_queue_event_time[
                        tracker_id
                    ] = current_time

                # =====================================
                # BILLING_QUEUE_EXIT
                # =====================================

                elif (

                    tracker_id in queue_entered

                    and current_zone != "BILLING_QUEUE"

                    and cooldown_passed
                ):

                    create_event(

                        visitor_id=visitor_id,

                        camera_id=camera_id,

                        event_type="BILLING_QUEUE_EXIT",

                        zone_id="BILLING_QUEUE"
                    )

                    queue_entered.remove(
                        tracker_id
                    )

                    last_queue_event_time[
                        tracker_id
                    ] = current_time

            # =========================================
            # SAVE / CLEAR STABLE ZONES
            # =========================================

            if current_zone:

                previous_zones[
                    tracker_id
                ] = current_zone

            else:

                if tracker_id in previous_zones:

                    del previous_zones[
                        tracker_id
                    ]

        # =============================================
        # DISPLAY
        # =============================================

        cv2.imshow(
            camera_id,
            frame
        )

        if cv2.waitKey(1) & 0xFF == ord("q"):

            break

        frame_count += 1

        # =============================================
        # LIMIT FRAMES
        # =============================================

        if frame_count > 300:

            break

    # =================================================
    # RELEASE VIDEO
    # =================================================

    cap.release()

# =====================================================
# CLOSE WINDOWS
# =====================================================

cv2.destroyAllWindows()

# =====================================================
# SORT EVENTS
# =====================================================

events.sort(
    key=lambda x: x["timestamp"]
)

# =====================================================
# SAVE EVENTS
# =====================================================

with open(OUTPUT_PATH, "w") as f:

    for event in events:

        f.write(
            json.dumps(event)
            + "\n"
        )

print("\nFINAL events.jsonl saved")

print(f"\nSaved to: {OUTPUT_PATH}")

print(f"\nTotal Events: {len(events)}")

