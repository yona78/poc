# Video Metadata Monorepo

This repository hosts a Python monorepo intended for multiple microservices. At the moment it contains a single service that consumes video metadata messages from RabbitMQ, stores them in Elasticsearch, and exposes a CRUD HTTP API using FastAPI.

## Structure

- `libs/` – shared libraries for messaging, storage and data models.
- `services/video_metadata_service/` – FastAPI application handling RabbitMQ messages and HTTP requests.

The messaging and storage layers are accessed through abstract interfaces, allowing alternative backends (e.g., Kafka, MongoDB) to be injected without changing service code.

## Running the service

1. Install dependencies:
   ```bash
   pip install -e .
   ```
2. Run the API with Uvicorn:
   ```bash
   uvicorn services.video_metadata_service.app:app
   ```

The application will automatically start a background consumer for the `video_metadata` queue and index incoming messages into Elasticsearch.

## Development tools

To publish random video metadata messages for testing, run:

```bash
python tools/generate_mocks.py --count 5
```

This script creates valid `VideoMetadataDTO` payloads and sends them to the configured RabbitMQ queue.

## API documentation

Interactive Swagger UI is available once the service is running at:

```
http://localhost:8000/docs
```

To generate a standalone OpenAPI schema file, execute:

```bash
python tools/generate_openapi.py
```

The schema will be written to `docs/openapi.json`.
