# AI-Powered Retail Store Intelligence System

## Overview

The AI-Powered Retail Store Intelligence System transforms retail CCTV footage into actionable business intelligence using Computer Vision, Event Intelligence, Analytics APIs, and Real-Time Dashboards.

The system detects and tracks visitors, generates semantic behavioral events, correlates purchases from POS transactions, and exposes analytics through a FastAPI backend and Streamlit dashboard.

The solution is designed around a single business objective:

## North Star Metric

### Offline Store Conversion Rate

```text
Conversion Rate =
Purchasing Visitors ÷ Total Visitors
```

Every component in the system is designed to either improve the accuracy of this metric or make it more actionable for retail operations teams.

---

# Key Features

* Multi-store support
* YOLOv8-based person detection
* ByteTrack-based multi-object tracking
* Entry and Exit detection
* Zone intelligence and customer journey tracking
* Dwell time analytics
* Billing queue analytics
* Purchase correlation using POS data
* Funnel analytics
* Anomaly detection
* Real-time replay engine
* FastAPI analytics backend
* Streamlit dashboard
* SQLite persistence
* Batch ingestion APIs
* Health monitoring APIs
* Dockerized deployment

---

# Business Questions Answered

The system helps answer key retail questions:

| Business Question                         | System Component  |
| ----------------------------------------- | ----------------- |
| How many customers visited and purchased? | Metrics API       |
| Where are customers dropping off?         | Funnel Analytics  |
| Which zones receive attention?            | Heatmap Analytics |
| Are billing queues increasing?            | Queue Analytics   |
| Is conversion rate declining?             | Anomaly Detection |
| Is any feed stale or unhealthy?           | Health Endpoint   |

---

# System Architecture

```text
Retail Video
      ↓
YOLOv8 Detection
      ↓
ByteTrack Tracking
      ↓
Zone Intelligence
      ↓
Event Generation
      ↓
Purchase Correlation
      ↓
FastAPI Backend
      ↓
SQLite Database
      ↓
Streamlit Dashboard
```

---

# Event Types

The system generates semantic retail events:

* ENTRY
* EXIT
* ZONE_ENTER
* ZONE_EXIT
* ZONE_DWELL
* BILLING_QUEUE_JOIN
* BILLING_QUEUE_EXIT
* PURCHASE
* REENTRY

These events form the foundation for all downstream analytics.

---

# Project Structure

```text
project/
│
├── backend/
│   ├── app.py
│   ├── database.py
│   ├── replay.py
│   └── requirements.txt
│
├── dashboard/
│   └── dashboard.py
│
├── pipelines/
│   ├── generic_pipeline.py
│   └── purchase_correlator.py
│
├── configs/
│
├── data/
│
├── tests/
│   └── test_api.py
│
├── Dockerfile
├── docker-compose.yml
│
├── README.md
├── DESIGN.md
└── CHOICES.md
```

---

# AI Engineering Documentation

The project includes dedicated AI engineering documentation:

### DESIGN.md

Contains:

* Architecture overview
* Design rationale
* AI-assisted decisions
* Tradeoffs and future improvements

### CHOICES.md

Documents:

* Detection model selection
* Event schema design decisions
* API architecture choices
* Engineering tradeoffs

---

# Analytics APIs

## Health Monitoring

```http
GET /health
```

Monitors service health and stale feeds.

---

## Metrics

```http
GET /metrics
```

Provides:

* Visitors
* Purchases
* Revenue
* Conversion metrics

---

## Heatmap Analytics

```http
GET /heatmap
```

Provides zone-level engagement insights.

---

## Funnel Analytics

```http
GET /stores/{store_id}/funnel
```

Tracks customer progression through:

```text
ENTRY
→ ZONE ENGAGEMENT
→ BILLING
→ PURCHASE
```

---

## Event Ingestion

```http
POST /events/ingest
```

Single event ingestion.

---

## Batch Event Ingestion

```http
POST /events/batch_ingest
```

Bulk ingestion for scalable event streaming.

---

## Anomaly Detection

```http
GET /anomalies
```

Identifies:

* Queue spikes
* Conversion drops
* Operational anomalies

---

# Dashboard Features

The Streamlit dashboard provides:

* Visitor Analytics
* Purchase Analytics
* Revenue Monitoring
* Conversion Funnel
* Queue Monitoring
* Heatmap Analytics
* Store-level Insights
* Event Distribution
* Health Monitoring
* Anomaly Detection

---

# Testing

The project includes pytest-based validation.

Run tests:

```bash
pytest tests/
```

Covered edge cases:

* Empty store
* All-staff scenario
* Zero purchases
* Re-entry handling
* Health endpoint validation

---

# Running Locally

## Backend

```bash
cd backend
uvicorn app:app --reload
```

---

## Replay Engine

```bash
cd backend
python replay.py
```

---

## Dashboard

```bash
cd dashboard
streamlit run dashboard.py
```

---

# Docker Deployment (Recommended)

## Build

```bash
docker compose build
```

## Run

```bash
docker compose up
```

---

## Services

Backend API:

```text
http://localhost:8000/docs
```

Dashboard:

```text
http://localhost:8501
```

Health Endpoint:

```text
http://localhost:8000/health
```

---

# Technologies Used

* Python
* YOLOv8
* ByteTrack
* OpenCV
* FastAPI
* Streamlit
* SQLite
* Plotly
* Pandas
* Docker
* Docker Compose

---

# Challenge Deliverables

Included in this submission:

* Computer Vision Pipeline
* Event Intelligence Layer
* Purchase Correlation Engine
* FastAPI Analytics Backend
* Funnel Analytics
* Health Monitoring
* Batch Ingestion Support
* Streamlit Dashboard
* Dockerized Deployment
* README.md
* DESIGN.md
* CHOICES.md
* Pytest Test Suite

---

# Future Improvements

Potential future enhancements include:

* Staff identification using ReID
* Cross-camera identity stitching
* RTSP live stream ingestion
* Kafka-based event streaming
* Cloud deployment
* Distributed analytics infrastructure
* Advanced anomaly detection
* Vector search for event retrieval

---

# Conclusion

The AI-Powered Retail Store Intelligence System demonstrates how retail video can be transformed into actionable business intelligence through Computer Vision, Event Engineering, Analytics APIs, and Real-Time Dashboards.

By focusing on Offline Store Conversion Rate as the North Star Metric, the system connects low-level visual signals to meaningful business outcomes.

