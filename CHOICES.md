# Engineering Choices and Tradeoffs

## Overview

This document explains key engineering decisions, architectural tradeoffs, and implementation choices made during development of the AI Retail Store Intelligence System.

---

# 1. YOLOv8 for Detection

YOLOv8n was selected because it provides:

* fast inference
* lightweight deployment
* real-time capability
* easy integration with OpenCV

The nano model was preferred for CPU compatibility and faster local experimentation.

---

# 2. ByteTrack for Tracking

ByteTrack was used for multi-object tracking because:

* stable ID assignment
* lightweight integration
* strong real-time performance
* minimal configuration overhead

---

# 3. Semantic Event Architecture

Instead of storing raw detections only, the system generates semantic retail events such as:

* ENTRY
* ZONE_DWELL
* BILLING_QUEUE_JOIN
* PURCHASE

This makes downstream analytics significantly easier and closer to real production retail intelligence systems.

---

# 4. Zone Stabilization Buffer

A zone stabilization mechanism was introduced to reduce event flapping caused by centroid jitter and rapid boundary switching.

Visitors must remain in a candidate zone for a minimum stability duration before transitions are confirmed.

This significantly improved event quality.

---

# 5. Purchase Correlation Strategy

The provided POS dataset contained synthetic timestamps that did not perfectly align with replay-generated CV events.

To handle this, nearest billing queue matching was used instead of strict real-time timestamp correlation.

This approach was chosen to maintain realistic purchase attribution while working with synthetic challenge data.

---

# 6. SQLite for Persistence

SQLite was selected because:

* lightweight setup
* zero infrastructure dependency
* fast local experimentation
* simple deployment

For production-scale systems, PostgreSQL or distributed OLAP systems would be preferable.

---

# 7. Replay Engine

A replay architecture was implemented to simulate real-time streaming from offline generated events.

This enables:

* backend testing
* dashboard testing
* pipeline debugging
* event simulation

without requiring live camera feeds.

---

# 8. Batch Ingestion API

Batch ingestion support was added to improve scalability and reduce API overhead during replay streaming.

This is more representative of production event pipelines.

---

# 9. Funnel Analytics

Dedicated funnel APIs were implemented to support business-level retail analytics such as:

* visitor engagement
* billing conversion
* purchase conversion

This transforms raw CV events into actionable retail intelligence.

---

# 10. Staff Filtering Decision

A simplistic uniform-color heuristic was considered for staff detection.

However, because customer clothing can overlap with staff colors, fully enabling this logic risked introducing false positives.

Instead, the system keeps an extensible `is_staff` hook reserved for future improvements such as:

* ReID embeddings
* uniform classification
* dwell behavior analysis
* restricted-zone persistence

---

# 11. Dockerization

The system was containerized using Docker and Docker Compose to improve:

* reproducibility
* deployment portability
* local development consistency

---

# 12. Future Improvements

Potential future extensions include:

* Kafka streaming
* cloud deployment
* distributed analytics
* RTSP ingestion
* advanced ReID
* multi-camera identity stitching
* vector event search
* edge deployment
