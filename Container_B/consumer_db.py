import os
import json
import logging
import time
from datetime import datetime
from typing import Dict, Any
import pika
from dotenv import load_dotenv
from database import db_manager
from models import RedNotice


load_dotenv()


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RabbitMQConsumer:
    """RabbitMQ message consumer class"""
    
    def __init__(self):
        self.rabbitmq_host = os.getenv('RABBITMQ_HOST', 'container_c')
        self.rabbitmq_port = int(os.getenv('RABBITMQ_PORT', '5672'))
        self.rabbitmq_user = os.getenv('RABBITMQ_USER', 'guest')
        self.rabbitmq_password = os.getenv('RABBITMQ_PASSWORD', 'guest')
        self.queue_name = os.getenv('QUEUE_NAME', 'red_notices_queue')
        
        self.connection = None
        self.channel = None
        
    def connect(self):
        """Establish connection to RabbitMQ"""
        try:
            credentials = pika.PlainCredentials(self.rabbitmq_user, self.rabbitmq_password)
            parameters = pika.ConnectionParameters(
                host=self.rabbitmq_host,
                port=self.rabbitmq_port,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
         
            self.channel.queue_declare(
                queue=self.queue_name,
                durable=True
            )
            
            
            self.channel.basic_qos(prefetch_count=1)
            
            logger.info("Successfully connected to RabbitMQ")
            
        except Exception as e:
            logger.error(f"Error connecting to RabbitMQ: {e}")
            raise
    
    def callback(self, ch, method, properties, body):
        """Process received message"""
        try:
           
            message_data = json.loads(body.decode('utf-8'))
            logger.info(f"Processing message: {message_data.get('name', 'Unknown')}")
            
            
            session = db_manager.get_session()
            
            try:
                
                existing_record = session.query(RedNotice).filter(
                    RedNotice.name == message_data['name']
                ).first()
                
                if existing_record:
                   
                    existing_record.age = message_data.get('age')
                    existing_record.nationality = message_data.get('nationality')
                    existing_record.image_url = message_data.get('image_url')
                    existing_record.scraped_at = datetime.fromisoformat(message_data.get('scraped_at', datetime.now().isoformat()))
                    existing_record.updated_at = datetime.utcnow()
                    
                    session.commit()
                    logger.info(f"Updated existing record: {message_data.get('name')}")
                else:
                    
                    new_record = RedNotice(
                        name=message_data['name'],
                        age=message_data.get('age'),
                        nationality=message_data.get('nationality'),
                        image_url=message_data.get('image_url'),
                        scraped_at=datetime.fromisoformat(message_data.get('scraped_at', datetime.now().isoformat()))
                    )
                    
                    session.add(new_record)
                    session.commit()
                    logger.info(f"Created new record: {message_data.get('name')}")
                
                
                ch.basic_ack(delivery_tag=method.delivery_tag)
                
            except Exception as e:
                logger.error(f"Database error: {e}")
                session.rollback()
                
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    def start_consuming(self):
        """Start consuming messages"""
        try:
            
            self.channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=self.callback
            )
            
            logger.info("Starting to consume messages...")
            self.channel.start_consuming()
            
        except KeyboardInterrupt:
            logger.info("Stopping consumer...")
            self.stop_consuming()
        except Exception as e:
            logger.error(f"Error in consumer: {e}")
            self.stop_consuming()
    
    def stop_consuming(self):
        """Stop consuming messages"""
        if self.channel:
            self.channel.stop_consuming()
        
        if self.connection and self.connection.is_open:
            self.connection.close()
        
        logger.info("Consumer stopped")


def main():
    """Main function"""
    try:
        
        db_manager.create_tables()
        logger.info("Database initialized")
        
        
        consumer = RabbitMQConsumer()
        consumer.connect()
        consumer.start_consuming()
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
    finally:
        
        db_manager.close_session()
        db_manager.close_engine()


if __name__ == "__main__":
    main()
