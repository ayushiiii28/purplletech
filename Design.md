# DESIGN.md

# Purplle Store Intelligence System - Design Document

## Problem Statement

Retail stores generate large volumes of CCTV footage, but extracting actionable business insights from this data remains challenging. The objective of this project is to convert raw video streams into structured customer behavior analytics that help measure store performance, customer engagement, queue efficiency, and conversion rates.

The system processes multi-camera retail footage, generates behavioral events, correlates them with POS transactions, and exposes analytics through APIs and a live dashboard.

---

# High-Level Architecture

```text
Video Footage
      |
      v
YOLOv8 Detection + Tracking
      |
      v
Zone & Event Generation
      |
      v
Unified Event Stream
      |
      +----------------+
      |                |
      v                v
Purchase         Replay Service
Correlation            |
      |                |
      +---------> FastAPI Backend
                         |
                  SQLite Database
                         |
                         v
                 Streamlit Dashboard
```

---

# System Components

## 1. Detection Pipeline

The detection pipeline processes CCTV footage from:

* Entry Cameras
* Floor Cameras
* Billing Cameras

YOLOv8 is used to detect people in each frame.

Tracking logic assigns a persistent visitor identifier to each detected individual.

Using store-specific configuration files, visitor coordinates are mapped to predefined store zones such as:

* Entry Gate
* Center Kiosk
* Makeup Table
* Billing Queue

The pipeline generates business-level events instead of storing raw detections.

Examples:

* ENTRY
* EXIT
* ZONE_ENTER
* ZONE_EXIT
* ZONE_DWELL
* BILLING_QUEUE_JOIN
* PURCHASE

---

## 2. Event Stream

All generated events are stored in a unified JSONL event stream.

Each event follows a common schema:

```json
{
  "event_id": "...",
  "store_id": "...",
  "camera_id": "...",
  "visitor_id": "...",
  "event_type": "...",
  "timestamp": "...",
  "zone_id": "...",
  "confidence": 0.95,
  "metadata": {}
}
```

Using an event-based architecture provides:

* Lower storage requirements
* Easier analytics computation
* Decoupled system components
* Better scalability

---

## 3. Purchase Correlation

The provided POS dataset does not contain direct visitor identifiers.

To estimate customer conversion:

1. Billing queue events are identified.
2. POS transactions are loaded.
3. Recent billing visitors are matched to transactions.
4. PURCHASE events are generated.

This enables:

* Conversion rate measurement
* Funnel analytics
* Revenue attribution

---

## 4. FastAPI Backend

The backend serves as the analytics engine.

Responsibilities:

### Event Ingestion

* POST /events/ingest
* POST /events/batch_ingest

### Analytics

* GET /metrics
* GET /heatmap
* GET /anomalies
* GET /stores/{store_id}/metrics
* GET /stores/{store_id}/funnel

### Monitoring

* GET /health

SQLite is used as the persistence layer.

---

## 5. Dashboard

A Streamlit dashboard provides live visibility into store performance.

Metrics displayed include:

* Total Events
* Unique Visitors
* Purchases
* Revenue
* Conversion Rate
* Funnel Analytics
* Zone Activity

The dashboard continuously consumes backend APIs and updates in real time.

---

# Key Design Decisions

## Event-Based Analytics

Instead of storing every frame-level detection, the system stores meaningful business events.

Benefits:

* Reduced storage usage
* Simpler analytics
* Faster querying
* Easier debugging

---

## Batch Event Ingestion

A batch ingestion endpoint was implemented to support efficient event replay and future scalability.

Benefits:

* Lower API overhead
* Higher throughput
* Improved deployment readiness

---

## Multi-Store Configuration

Store-specific configurations are stored separately.

Benefits:

* Reusable pipeline
* Easier onboarding of new stores
* Cleaner architecture

---

# AI-Assisted Decisions

AI tools were used during development for brainstorming architectural approaches, reviewing implementation choices, and identifying edge cases.

All final engineering decisions were manually reviewed and adapted.

### Detection Model Selection

Alternative models considered:

* YOLOv8
* RT-DETR
* YOLOv9

YOLOv8 was selected because of:

* Fast inference speed
* Mature ecosystem
* Strong documentation
* Easy deployment

### Event-Based Architecture

AI suggested storing either:

* Raw tracking data
* Business events

Business events were selected because they directly support retail analytics use cases.

### Purchase Correlation

AI suggested probabilistic matching and time-window matching.

Time-window matching was selected due to the absence of customer identifiers in the dataset and the limited scope of the challenge.

---

# Edge Cases

The system considers several edge cases:

### Group Entry

Each tracked individual receives a unique visitor identifier.

### Queue Activity

Billing queue joins and exits are tracked separately from general zone movement.

### Empty Store Periods

Analytics endpoints remain functional even when no visitors are present.

### Re-Entry

Basic re-entry logic is implemented through visitor session tracking.

### Staff Detection

The schema supports staff classification through the is_staff field.

For this submission, staff classification remains a placeholder and is reserved for future enhancement using:

* Uniform classification
* Re-identification models
* Appearance embeddings

---

# Scalability

Current implementation:

* SQLite
* Local replay simulation
* Single FastAPI instance

Future production enhancements:

* PostgreSQL
* Kafka event streaming
* Redis caching
* Multi-region deployment
* Distributed tracking services

---

# Limitations

* Staff detection is not fully implemented.
* Re-entry detection is heuristic based.
* Purchase correlation uses simplified matching.
* Zone stability filtering can be improved further.
* Anomaly detection is rule-based.

These trade-offs were intentionally made to prioritize a complete end-to-end working solution within the challenge timeframe.

---

# Conclusion

The system successfully transforms raw CCTV footage into actionable retail intelligence. It provides customer movement analytics, funnel tracking, queue monitoring, purchase attribution, real-time dashboards, and production-style APIs while remaining fully reproducible through Docker Compose.
