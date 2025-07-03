import os
import time
import json
import logging
from datetime import datetime
from typing import List, Dict, Any
import pika
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class InterpolScraper:
    """Interpol Red Notices scraper class using Selenium"""
    
    def __init__(self):
        self.base_url = "https://www.interpol.int/How-we-work/Notices/Red-Notices/View-Red-Notices/"
        self.driver = None
        
    def setup_driver(self):
        """Setup Chrome driver with options"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)
        
    def scrape_red_notices(self) -> List[Dict[str, Any]]:
        """Scrape red notices from Interpol website using Selenium with pagination"""
        try:
            logger.info("Starting to scrape Interpol Red Notices with Selenium")
            
            if not self.driver:
                self.setup_driver()
                
            if not self.driver:
                logger.error("Failed to setup driver")
                return []
                
            self.driver.get(self.base_url)
            time.sleep(5)  # Wait for page to load
            
            red_notices = []
            page = 1
            max_pages = 50  # Limit to prevent infinite loop
            
            while page <= max_pages:
                logger.info(f"Scraping page {page}")
                
                # Wait for red notices to load
                try:
                    WebDriverWait(self.driver, 20).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "redNoticeItem"))
                    )
                except:
                    logger.warning(f"No red notices found on page {page}")
                    break
                
                # Find all red notice items on current page
                notice_items = self.driver.find_elements(By.CLASS_NAME, "redNoticeItem")
                logger.info(f"Found {len(notice_items)} red notice items on page {page}")
                
                for item in notice_items:
                    try:
                        name = "Unknown"
                        try:
                            name_element = item.find_element(By.CSS_SELECTOR, "a.redNoticeItem__labelLink")
                            name = name_element.text.strip()
                        except:
                            try:
                                name_element = item.find_element(By.CSS_SELECTOR, ".redNoticeItem__label")
                                name = name_element.text.strip()
                            except:
                                try:
                                    name_element = item.find_element(By.CSS_SELECTOR, "h3, h4, .name")
                                    name = name_element.text.strip()
                                except:
                                    pass
                        age = "Unknown"
                        try:
                            age_element = item.find_element(By.CSS_SELECTOR, ".age, .redNoticeItem__age")
                            age = age_element.text.strip()
                        except:
                            pass
                        nationality = "Unknown"
                        try:
                            nationality_element = item.find_element(By.CSS_SELECTOR, ".nationalities, .redNoticeItem__nationalities")
                            nationality = nationality_element.text.strip()
                        except:
                            pass
                        image_url = None
                        try:
                            img_element = item.find_element(By.CSS_SELECTOR, "img")
                            image_url = img_element.get_attribute("src")
                        except:
                            pass
                        if name and name != "Unknown":
                            red_notice = {
                                'name': name,
                                'age': age,
                                'nationality': nationality,
                                'image_url': image_url,
                                'scraped_at': datetime.now().isoformat()
                            }
                            red_notices.append(red_notice)
                            logger.info(f"Scraped: {name} - {age} - {nationality}")
                    except Exception as e:
                        logger.error(f"Error processing notice item: {e}")
                        continue
                
                # Try to go to next page (daha sağlam ve esnek)
                next_button = None
                next_selectors = [
                    ".nextElement",
                    ".pagination-next",
                    ".next",
                    "[aria-label='Next']",
                    "li.next > a",
                    "a[rel='next']"
                ]
                for selector in next_selectors:
                    try:
                        btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if btn and btn.is_displayed() and btn.is_enabled():
                            next_button = btn
                            break
                    except Exception:
                        continue
                if next_button:
                    try:
                        next_button.click()
                        logger.info(f"Clicked next button with selector: {selector}")
                        time.sleep(3)  # Wait for page to load
                        page += 1
                    except Exception as e:
                        logger.warning(f"Next button found but could not be clicked: {e}")
                        break
                else:
                    logger.info("No next page button found or button is not enabled/visible, stopping pagination")
                    break
            
            logger.info(f"Successfully scraped {len(red_notices)} red notices from {page-1} pages")
            return red_notices
            
        except Exception as e:
            logger.error(f"Error scraping red notices: {e}")
            return []
        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None


class RabbitMQProducer:
    """RabbitMQ message producer class"""
    
    def __init__(self):
        self.rabbitmq_host = os.getenv('RABBITMQ_HOST', 'container_c')
        self.rabbitmq_port = int(os.getenv('RABBITMQ_PORT', '5672'))
        self.rabbitmq_user = os.getenv('RABBITMQ_USER', 'guest')
        self.rabbitmq_password = os.getenv('RABBITMQ_PASSWORD', 'guest')
        self.queue_name = os.getenv('QUEUE_NAME', 'red_notices_queue')
        
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
            
            # Declare queue
            self.channel.queue_declare(
                queue=self.queue_name,
                durable=True
            )
            
            logger.info("Successfully connected to RabbitMQ")
            
        except Exception as e:
            logger.error(f"Error connecting to RabbitMQ: {e}")
            raise
    
    def send_message(self, message: Dict[str, Any]):
        """Send message to RabbitMQ queue"""
        try:
            message_body = json.dumps(message)
            self.channel.basic_publish(
                exchange='',
                routing_key=self.queue_name,
                body=message_body,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                    content_type='application/json'
                )
            )
            logger.info(f"Sent message: {message.get('name', 'Unknown')}")
            
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            raise
    
    def close(self):
        """Close RabbitMQ connection"""
        if hasattr(self, 'connection') and self.connection.is_open:
            self.connection.close()
            logger.info("RabbitMQ connection closed")


class InterpolDataCollector:
    """Main data collector class"""
    
    def __init__(self):
        self.scraper = InterpolScraper()
        self.producer = RabbitMQProducer()
        self.interval = int(os.getenv('SCRAPING_INTERVAL', '300'))  # 5 minutes default
        
    def run(self):
        """Main run loop"""
        logger.info(f"Starting Interpol Data Collector with {self.interval}s interval (Selenium mode)")
        
        while True:
            try:
                # Scrape data
                red_notices = self.scraper.scrape_red_notices()
                
                if red_notices:
                    # Connect to RabbitMQ
                    self.producer.connect()
                    
                    # Send each notice to queue
                    for notice in red_notices:
                        self.producer.send_message(notice)
                    
                    # Close connection
                    self.producer.close()
                    
                    logger.info(f"Successfully processed {len(red_notices)} red notices")
                else:
                    logger.warning("No red notices found")
                
                # Wait for next interval
                logger.info(f"Waiting {self.interval} seconds before next scrape")
                time.sleep(self.interval)
                
            except KeyboardInterrupt:
                logger.info("Shutting down Interpol Data Collector")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(60)  # Wait 1 minute before retrying


if __name__ == "__main__":
    collector = InterpolDataCollector()
    collector.run()
