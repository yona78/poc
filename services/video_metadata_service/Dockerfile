FROM python:3.11-slim

WORKDIR /app

COPY . .
RUN pip install --no-cache-dir -e .

CMD ["uvicorn", "services.video_metadata_service.app:app", "--host", "0.0.0.0", "--port", "8000"]
