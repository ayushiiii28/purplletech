# AI-Powered Retail Store Intelligence System

## Overview

This project is a production-inspired AI retail analytics system designed to monitor in-store customer behavior using computer vision, event engineering, analytics APIs, and real-time dashboards.

The system processes retail store video feeds, tracks visitors, generates semantic behavioral events, correlates POS purchases, and exposes analytics through FastAPI and Streamlit dashboards.

---

# Features

* Multi-store support
* YOLOv8-based person detection
* ByteTrack-based multi-object tracking
* Zone intelligence
* Queue analytics
* Dwell time analytics
* Purchase correlation
* Funnel analytics
* Real-time replay engine
* FastAPI backend
* Streamlit analytics dashboard
* SQLite persistence
* Batch ingestion APIs
* Health monitoring APIs

---

# System Architecture

```text
Camera Feed
    ↓
YOLOv8 Detection
    ↓
ByteTrack Tracking
    ↓
Zone Intelligence Engine
    ↓
Event Generation
    ↓
FastAPI Backend
    ↓
SQLite Database
    ↓
Analytics Dashboard
```

---

# Event Types

The system generates semantic retail events including:

* ENTRY
* EXIT
* ZONE_ENTER
* ZONE_EXIT
* ZONE_DWELL
* BILLING_QUEUE_JOIN
* BILLING_QUEUE_EXIT
* PURCHASE
* REENTRY

---

# Folder Structure

```text
project/
│
├── app.py
├── dashboard.py
├── replay.py
├── purchase_correlator.py
├── generic_pipeline.py
├── database.py
│
├── configs/
├── data/
├── videos/
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
│
├── README.md
└── CHOICES.md
```

---

# APIs

## Health

```http
GET /health
```

## Metrics

```http
GET /metrics
```

## Heatmap

```http
GET /heatmap
```

## Funnel Analytics

```http
GET /stores/{store_id}/funnel
```

## Event Ingestion

```http
POST /events/ingest
```

## Batch Event Ingestion

```http
POST /events/batch_ingest
```

---

# Running the System

## 1. Start Backend

```bash
uvicorn app:app --reload
```

## 2. Replay Events

```bash
python replay.py
```

## 3. Launch Dashboard

```bash
streamlit run dashboard.py
```

---

# Docker Setup

## Build

```bash
docker compose build
```

## Run

```bash
docker compose up
```

---

# Dashboard Features

* Visitor analytics
* Conversion funnel
* Revenue metrics
* Queue monitoring
* Heatmaps
* Camera-wise analytics
* Store-wise analytics
* Event distribution
* Anomaly detection

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
* Docker

---

# Future Improvements

* Real RTSP stream ingestion
* Kafka-based event streaming
* ReID-based visitor tracking
* Staff recognition
* Cloud deployment
* Distributed analytics pipeline
* Vector search for event retrieval


