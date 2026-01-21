import pika
import json
import os
import time
import sys
from sqlalchemy.orm import Session
from database import SessionLocal
import models
import video_processor

# Configurações
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://user:password@rabbitmq:5672/")
QUEUE_NAME = "video_processing"
SHARED_DIR = os.getenv("SHARED_DIR", "/data")
UPLOADS_DIR = os.path.join(SHARED_DIR, "uploads")
OUTPUTS_DIR = os.path.join(SHARED_DIR, "outputs")

# Garantir que diretórios existam
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)

def update_video_status(video_id: int, status: models.VideoStatus, zip_path: str = None):
    db: Session = SessionLocal()
    try:
        video = db.query(models.Video).filter(models.Video.id == video_id).first()
        if video:
            video.status = status
            if zip_path:
                video.zip_path = zip_path
            db.commit()
    except Exception as e:
        print(f"Erro ao atualizar banco de dados: {e}")
    finally:
        db.close()

def callback(ch, method, properties, body):
    print(f" [x] Recebido: {body}")
    data = json.loads(body)
    
    video_id = data.get("video_id")
    filename = data.get("filename")
    
    if not video_id or not filename:
        print("Mensagem inválida.")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    video_path = os.path.join(UPLOADS_DIR, filename)
    
    if not os.path.exists(video_path):
        print(f"Erro: Arquivo não encontrado: {video_path}")
        update_video_status(video_id, models.VideoStatus.ERROR)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    # Atualiza status para PROCESSING
    update_video_status(video_id, models.VideoStatus.PROCESSING)
    
    try:
        # Processa o vídeo
        zip_filename = video_processor.process_video_file(video_path, OUTPUTS_DIR)
        
        # Atualiza status para COMPLETED
        update_video_status(video_id, models.VideoStatus.COMPLETED, zip_filename)
        print(f" [x] Processamento concluído para vídeo ID {video_id}")
        
    except Exception as e:
        print(f"Erro no processamento: {e}")
        update_video_status(video_id, models.VideoStatus.ERROR)
        
    finally:
        # Confirma processamento da mensagem
        ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    print("🎬 Video Worker connecting to RabbitMQ...")
    
    # Retry logic connection
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
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)