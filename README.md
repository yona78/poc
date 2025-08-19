# Video Metadata Monorepo

This repository hosts a Python monorepo intended for multiple microservices. It currently contains:

- **video_metadata_service** – consumes video metadata messages from RabbitMQ, stores them in Elasticsearch, and exposes a read/update/delete HTTP API using FastAPI.
- **filter_service** – reads messages from a general queue, filters them by `video_id`, and forwards matches to an algorithm-specific queue.

## Structure

- `libs/` – shared libraries for messaging, storage and data models.
- `services/video_metadata_service/` – FastAPI application handling RabbitMQ messages and HTTP requests.
- `services/filter_service/` – RabbitMQ filter that routes messages to algorithm queues.

The messaging and storage layers are accessed through abstract, type-aware interfaces. Concrete RabbitMQ, Elasticsearch, and MongoDB implementations operate on generic Pydantic models, making it easy to plug in alternative backends or DTOs.

## Configuration

Each microservice reads its configuration from a dedicated `.env` file at the repository root:

- `.env.video_metadata_service` – RabbitMQ, Elasticsearch, MongoDB, and log settings for the API service.
- `.env.filter_service` – RabbitMQ queues, target `video_id`, and log settings for the filter.

Settings are validated with Pydantic so missing values cause an early failure.

## Running the service

1. Install dependencies:
   ```bash
   pip install -e .
   ```
   This installs the project in editable mode so the shared `libs` and service packages are available on the Python path.
2. Copy `.env.video_metadata_service` and `.env.filter_service` and adjust any values as needed.
3. Run the services with Uvicorn:
   ```bash
   uvicorn services.video_metadata_service.app:app
   uvicorn services.filter_service.app:app --port 8001
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

Application logs are JSON-formatted with configurable levels and optional `labels`. Logs are written to the console and to a dedicated Elasticsearch index specified by `LOG_ELASTICSEARCH_URL` and `LOG_ELASTICSEARCH_INDEX` in each service's env file.

## Docker deployment

1. Adjust the env files as needed.
2. Build and run the stack with Docker Compose:
   ```bash
   docker compose up --build
   ```
   The service will be available at [http://localhost:8000](http://localhost:8000).

The compose file also launches RabbitMQ, Elasticsearch, and MongoDB containers used by the service.
