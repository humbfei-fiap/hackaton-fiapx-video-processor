import pika
import json
import os
import time
import sys
from database import SessionLocal
import models
from src.adapters.db.repositories import PostgresVideoRepository
from src.adapters.video.opencv_processor import OpenCVVideoProcessor
from src.use_cases.process_video import ProcessVideoUseCase

# Configurações
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://user:password@rabbitmq:5672/")
QUEUE_NAME = "video_processing"
SHARED_DIR = os.getenv("SHARED_DIR", "/data")
UPLOADS_DIR = os.path.join(SHARED_DIR, "uploads")
OUTPUTS_DIR = os.path.join(SHARED_DIR, "outputs")

# Garantir que diretórios existam
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)

def callback(ch, method, properties, body):
    print(f" [x] Recebido: {body}")
    data = json.loads(body)
    
    video_id = data.get("video_id")
    filename = data.get("filename")
    
    if not video_id or not filename:
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    # Dependency Injection
    db_session = SessionLocal()
    try:
        repo = PostgresVideoRepository(db_session)
        processor = OpenCVVideoProcessor()
        use_case = ProcessVideoUseCase(repo, processor, UPLOADS_DIR, OUTPUTS_DIR)
        
        use_case.execute(video_id, filename)
        print(f" [x] Processamento concluído para vídeo ID {video_id}")
        
    except Exception as e:
        print(f"Critical error in worker: {e}")
    finally:
        db_session.close()
        ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    print("🎬 Video Worker connecting to RabbitMQ (Clean Arch)...")
    
    while True:
        try:
            params = pika.URLParameters(RABBITMQ_URL)
            connection = pika.BlockingConnection(params)
            channel = connection.channel()
            break
        except pika.exceptions.AMQPConnectionError:
            print("RabbitMQ indisponível, tentando novamente em 5s...")
            time.sleep(5)
            
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.basic_qos(prefetch_count=1)
    
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)
    
    channel.start_consuming()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
