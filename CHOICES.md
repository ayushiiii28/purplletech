# CHOICES.md

# Engineering Choices and Tradeoffs

## Decision 1: Detection Model Selection

### Options Considered

* YOLOv8n
* YOLOv8s
* RT-DETR
* YOLOv9

### AI Suggestion

AI-assisted exploration suggested YOLOv8 because it offered the best balance between accuracy, inference speed, deployment simplicity, and ecosystem maturity.

### Final Choice

YOLOv8n

### Why

The challenge required processing retail footage efficiently on local hardware. YOLOv8n provided:

* Fast inference
* CPU-friendly execution
* Easy OpenCV integration
* Strong community support

While larger models could improve accuracy, they would increase latency and deployment complexity.

---

## Decision 2: Event Schema Design

### Options Considered

#### Option A

Store raw frame detections:

```json
{
  "frame_id": 101,
  "bbox": [...]
}
```

#### Option B

Generate business-level events:

```json
{
  "event_type": "ZONE_ENTER"
}
```

### AI Suggestion

AI recommended an event-based architecture because the downstream requirements focused on analytics rather than computer vision outputs.

### Final Choice

Business-level event architecture.

### Why

This reduced storage requirements and made metrics, funnel analytics, anomaly detection, and dashboard visualization significantly easier to implement.

Examples:

* ENTRY
* EXIT
* ZONE_ENTER
* BILLING_QUEUE_JOIN
* PURCHASE

---

## Decision 3: API Architecture

### Options Considered

#### Option A

Compute metrics directly from raw files.

#### Option B

Expose a dedicated analytics API layer.

### AI Suggestion

AI suggested separating analytics from the detection pipeline through a service layer exposed by REST endpoints.

### Final Choice

FastAPI-based analytics service.

### Why

Benefits included:

* Clear separation of concerns
* Easier dashboard integration
* Scalable architecture
* Independent testing of analytics logic

Endpoints include:

* /events/ingest
* /events/batch_ingest
* /stores/{store_id}/metrics
* /stores/{store_id}/funnel
* /health

---

## Additional Engineering Tradeoffs

### Zone Stabilization Buffer

A stabilization buffer was added to reduce rapid zone switching caused by tracking jitter.

### Purchase Correlation

Nearest billing queue matching was used because POS timestamps and synthetic CV timestamps were not perfectly aligned.

### Staff Detection

A simple color-based staff classifier was considered but rejected due to high false-positive risk. The system retains an extensible is_staff field for future ReID-based approaches.

### Database Choice

SQLite was selected for simplicity and portability. PostgreSQL would be preferred in production environments.

### Deployment

Docker and Docker Compose were used to ensure reproducibility and simplify evaluation.
