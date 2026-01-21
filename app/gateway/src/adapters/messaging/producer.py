import pika
import json
from src.ports.interfaces import MessageBroker

class RabbitMQProducer(MessageBroker):
    def __init__(self, broker_url: str, queue_name: str):
        self.broker_url = broker_url
        self.queue_name = queue_name

    def publish_video_processing(self, video_id: int, filename: str):
        params = pika.URLParameters(self.broker_url)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue=self.queue_name, durable=True)
        
        message = {"video_id": video_id, "filename": filename}
        
        channel.basic_publish(
            exchange='',
            routing_key=self.queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        connection.close()
