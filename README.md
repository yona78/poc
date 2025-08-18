# Video Metadata Monorepo

This repository hosts a Python monorepo intended for multiple microservices. At the moment it contains a single service that consumes video metadata messages from RabbitMQ, stores them in Elasticsearch, and exposes a read/update/delete HTTP API using FastAPI.

## Structure

- `libs/` – shared libraries for messaging, storage and data models.
- `services/video_metadata_service/` – FastAPI application handling RabbitMQ messages and HTTP requests.

The messaging and storage layers are accessed through abstract interfaces, allowing alternative backends (e.g., Kafka, MongoDB) to be injected without changing service code.

## Configuration

Environment variables are validated on startup using Pydantic settings. Required variables:

- `RABBITMQ_URL` / `VIDEO_METADATA_QUEUE`
- `ELASTICSEARCH_URL` / `ELASTICSEARCH_INDEX`
- `LOG_ELASTICSEARCH_URL` / `LOG_ELASTICSEARCH_INDEX`
- `MONGODB_URL` / `MONGODB_DB` / `MONGODB_COLLECTION`

Missing values will cause the service to fail fast with a validation error.

## Running the service

1. Install dependencies:
   ```bash
   pip install -e .
   ```
2. Define the required environment variables (RabbitMQ/Elasticsearch/MongoDB URLs, indices and queues).
3. Run the API with Uvicorn:
   ```bash
   uvicorn services.video_metadata_service.app:app
   ```

The application will automatically start a background consumer for the `video_metadata` queue and index incoming messages into Elasticsearch. API clients cannot create records directly; new metadata is only persisted when received from RabbitMQ.

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

## Advanced querying

Complex queries can be issued against the metadata index using raw Elasticsearch DSL:

```bash
curl 'http://localhost:8000/videos/search?query={"query":{"match_all":{}}}'
```

The `/videos/search_with_mongo` endpoint performs the same search and enriches each hit with a document from MongoDB sharing the same `video_id`.

## Logging

Application logs are written to the console and to a dedicated Elasticsearch index specified by `LOG_ELASTICSEARCH_URL` and `LOG_ELASTICSEARCH_INDEX`.
