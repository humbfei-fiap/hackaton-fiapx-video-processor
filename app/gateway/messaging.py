import pika
import json
import os

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://user:password@rabbitmq:5672/")
QUEUE_NAME = "video_processing"

def send_to_queue(video_id: int, filename: str):
    params = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    message = {
        "video_id": video_id,
        "filename": filename
    }

    channel.basic_publish(
        exchange='',
        routing_key=QUEUE_NAME,
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
        )
    )
    connection.close()
