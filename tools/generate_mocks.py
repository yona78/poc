#!/usr/bin/env python
import argparse
import json
import os
import random
import uuid
from datetime import datetime

import pika

from libs.models.video_metadata import (
    ActionRecognitionResultDTO,
    CompanyDTO,
    VideoMetadataWithActionsDTO,
)

ACTIONS = ["walking", "running", "jumping", "waving"]


def random_action_recognition() -> ActionRecognitionResultDTO:
    return ActionRecognitionResultDTO(
        frame_num=random.randint(0, 1000),
        timestamp=f"{random.randint(0,59):02d}:{random.randint(0,59):02d}:{random.randint(0,59):02d}.{random.randint(0,9)}",
        action=random.choice(ACTIONS),
        confidence=round(random.uniform(0.5, 1.0), 2),
        clip_length=random.choice([16, 32]),
    )


def random_company() -> CompanyDTO:
    return CompanyDTO(id=random.randint(1, 1000), name=random.choice(["acme", "globex"]))


def random_metadata() -> VideoMetadataWithActionsDTO:
    return VideoMetadataWithActionsDTO(
        video_id=str(uuid.uuid4()),
        timestamp=datetime.utcnow(),
        company=random_company(),
        actions=[random_action_recognition() for _ in range(random.randint(1, 3))],
    )


def publish_message(meta: VideoMetadataWithActionsDTO, url: str, queue: str) -> None:
    connection = pika.BlockingConnection(pika.URLParameters(url))
    channel = connection.channel()
    channel.queue_declare(queue=queue, durable=True)
    channel.basic_publish(exchange="", routing_key=queue, body=meta.json())
    connection.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish random video metadata mocks")
    parser.add_argument("--count", type=int, default=1, help="Number of messages to send")
    parser.add_argument(
        "--url",
        default=os.getenv("BROKER_URL", "amqp://guest:guest@localhost:5672/"),
        help="Message broker connection URL",
    )
    parser.add_argument(
        "--queue",
        default=os.getenv("VIDEO_METADATA_QUEUE", "video_metadata"),
        help="Queue name",
    )
    args = parser.parse_args()

    for _ in range(args.count):
        meta = random_metadata()
        publish_message(meta, args.url, args.queue)
        print(json.dumps(json.loads(meta.json()), indent=2))


if __name__ == "__main__":
    main()
