# Video Metadata Monorepo

This repository hosts a Python monorepo intended for multiple microservices. It currently contains:

- **ingest_service** – consumes video metadata messages from RabbitMQ and persists them to Elasticsearch.
- **video_metadata_service** – read-only FastAPI API for querying stored metadata and optional MongoDB enrichment.
- **filter_service** – reads messages from a general queue, filters them by configurable `video_id` values, and forwards matches to an algorithm-specific queue.

## Structure

- `libs/` – shared libraries for messaging, database access and data models.
- `services/ingest_service/` – background consumer that stores incoming metadata.
- `services/video_metadata_service/` – FastAPI application exposing read-only HTTP endpoints.
- `services/filter_service/` – message filter that routes messages to algorithm queues.

The messaging and database layers are accessed through abstract, type-aware interfaces. Concrete RabbitMQ, Elasticsearch, and MongoDB implementations operate on generic Pydantic models, making it easy to plug in alternative backends or DTOs.

## Configuration

Each microservice ships with its own `.env` file inside its service directory:

- `services/ingest_service/.env` – broker, Elasticsearch, MongoDB, and log settings for the ingest service. Broker
  configuration is split into `BROKER_HOST`, `BROKER_PORT`, `BROKER_USER`, and `BROKER_PASSWORD` variables instead of
  a single connection URL.
- `services/video_metadata_service/.env` – Elasticsearch, MongoDB, and log settings for the API service.
- `services/filter_service/.env` – queues, target `video_id` list, and log settings for the filter. It uses the same
  separate RabbitMQ variables (`BROKER_HOST`, `BROKER_PORT`, `BROKER_USER`, `BROKER_PASSWORD`).

Settings are validated with Pydantic so missing values cause an early failure.

The concrete message broker and database backend are selected globally via the
`MESSAGE_BROKER` and `DATABASE_BACKEND` environment variables. Switching from
RabbitMQ to another broker or from Elasticsearch to a different database only
requires changing these variables without modifying service code.

## Running the service

1. Install dependencies:
   ```bash
   pip install -e .
   ```
   This installs the project in editable mode so the shared `libs` and service packages are available on the Python path.
2. Copy the env files above and adjust any values as needed.
3. Run the services:
   ```bash
   python -m services.ingest_service.app
   uvicorn services.video_metadata_service.app:app
   uvicorn services.filter_service.app:app --port 8001
   ```

The ingest service consumes the `video_metadata` queue and indexes incoming messages into Elasticsearch. API clients cannot create records directly; new metadata is only persisted when received from the message broker.

## Development tools

To publish random video metadata messages for testing, run:

```bash
python tools/generate_mocks.py --count 5
```

This script creates valid `VideoMetadataWithActionsDTO` payloads and sends them to the configured RabbitMQ queue.

To exercise the filter service's source queue, a separate helper can publish plain `VideoMetadataDTO` messages:

```bash
python tools/generate_filter_mocks.py --count 5
```

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

Complex queries can be issued against the metadata index by sending raw Elasticsearch DSL in the request body:

```bash
curl -X GET 'http://localhost:8000/videos/search' \
  -H 'Content-Type: application/json' \
  -d '{"query":{"match_all":{}}}'
```

The `/videos/search_with_mongo` endpoint performs the same search and enriches each hit with a document from MongoDB sharing the same `video_id`:

```bash
curl -X GET 'http://localhost:8000/videos/search_with_mongo' \
  -H 'Content-Type: application/json' \
  -d '{"query":{"match_all":{}}}'
```

## Logging

Application logs are JSON-formatted with ECS base fields (`@timestamp`, `log.level`, `message`) and optional `labels`. Logs are written to the console and to a dedicated Elasticsearch index specified by `LOG_ELASTICSEARCH_URL` and `LOG_ELASTICSEARCH_INDEX` in each service's env file.

## Docker deployment

1. Adjust the env files as needed.
2. Build and run the stack with Docker Compose:
   ```bash
   docker compose up --build
   ```
   The service will be available at [http://localhost:8000](http://localhost:8000).

The compose file also launches RabbitMQ, Elasticsearch, and MongoDB containers used by the service.
