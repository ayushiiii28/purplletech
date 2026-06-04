FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY dashboard/ ./dashboard/
COPY data/ ./data/

EXPOSE 8000
EXPOSE 8501

