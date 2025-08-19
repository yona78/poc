#!/usr/bin/env python
import argparse
import json
import os
import random
import uuid
from datetime import datetime

import pika

from libs.models.video_metadata import CompanyDTO, VideoMetadataDTO

ACTIONS = ["walking", "running", "jumping", "waving"]


def random_company() -> CompanyDTO:
    return CompanyDTO(id=random.randint(1, 1000), name=random.choice(["acme", "globex"]))


def random_metadata(video_id: str | None = None) -> VideoMetadataDTO:
    return VideoMetadataDTO(
        video_id=video_id or str(uuid.uuid4()),
        timestamp=datetime.utcnow(),
        company=random_company(),
    )


def publish_message(meta: VideoMetadataDTO, host: str, port: int, username: str, password: str, queue: str) -> None:
    credentials = pika.PlainCredentials(username, password)
    params = pika.ConnectionParameters(host=host, port=port, credentials=credentials)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue=queue, durable=True)
    channel.basic_publish(exchange="", routing_key=queue, body=meta.json())
    connection.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish random filter messages")
    parser.add_argument("--count", type=int, default=1)
    parser.add_argument("--video-id", help="Use a specific video_id", default=None)
    parser.add_argument("--host", default=os.getenv("BROKER_HOST", "localhost"))
    parser.add_argument("--port", type=int, default=int(os.getenv("BROKER_PORT", "5672")))
    parser.add_argument("--username", default=os.getenv("BROKER_USER", "guest"))
    parser.add_argument("--password", default=os.getenv("BROKER_PASSWORD", "guest"))
    parser.add_argument("--queue", default=os.getenv("SOURCE_QUEUE", "video_metadata"))
    args = parser.parse_args()

    for _ in range(args.count):
        meta = random_metadata(args.video_id)
        publish_message(meta, args.host, args.port, args.username, args.password, args.queue)
        print(json.dumps(json.loads(meta.json()), indent=2))


if __name__ == "__main__":
    main()
