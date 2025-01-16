import pika
import logging
import os
import xml.etree.ElementTree as ET
import pg8000

# RabbitMQ Configuration
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "user")
RABBITMQ_PW = os.getenv("RABBITMQ_PW", "password")
QUEUE_NAME = 'xml_final'

# Database Configuration
DBHOST = os.getenv('DBHOST', 'localhost')
DBUSERNAME = os.getenv('DBUSERNAME', 'myuser')
DBPASSWORD = os.getenv('DBPASSWORD', 'mypassword')
DBNAME = os.getenv('DBNAME', 'mydatabase')
DBPORT = int(os.getenv('DBPORT', '5432'))

# Configure logging
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger()


def save_to_database(car_data):
    """Save extracted XML data to the database."""
    try:
        conn = pg8000.connect(
            host=DBHOST,
            port=DBPORT,
            database=DBNAME,
            user=DBUSERNAME,
            password=DBPASSWORD
        )
        cursor = conn.cursor()

        # Insert into Cars table
        cursor.execute("""
            INSERT INTO Cars (VIN, Condition, Odometer, MMR, Color, Interior)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (VIN) DO NOTHING;
        """, (
            car_data['VIN'],
            car_data['Condition'],
            car_data['Odometer'],
            car_data['MMR'],
            car_data['Color'],
            car_data['Interior']
        ))

        # Insert into Specifications table
        cursor.execute("""
            INSERT INTO Specifications (VIN, Year, Make, Model, Trim, Body, Transmission)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (VIN) DO NOTHING;
        """, (
            car_data['VIN'],
            car_data['Year'],
            car_data['Make'],
            car_data['Model'],
            car_data['Trim'],
            car_data['Body'],
            car_data['Transmission']
        ))

        # Insert into Sellers table
        cursor.execute("""
            INSERT INTO Sellers (VIN, Name, State, SaleDate, SellingPrice)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (VIN) DO NOTHING;
        """, (
            car_data['VIN'],
            car_data['SellerName'],
            car_data['State'],
            car_data['SaleDate'],
            car_data['SellingPrice']
        ))

        # Insert into Locations table
        cursor.execute("""
            INSERT INTO Locations (VIN, City, Latitude, Longitude)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (VIN) DO NOTHING;
        """, (
            car_data['VIN'],
            car_data['City'],
            car_data['Latitude'],
            car_data['Longitude']
        ))

        conn.commit()
        cursor.close()
        conn.close()
        logger.info(f"Data for VIN {car_data['VIN']} saved to the database.")
    except Exception as e:
        logger.error(f"Database save failed: {e}", exc_info=True)


def parse_xml_and_save(xml_content):
    """Parse XML content and save to the database."""
    try:
        root = ET.fromstring(xml_content)
        for car in root.findall('Car'):
            car_data = {
                'VIN': car.find('VIN').text,
                'Condition': int(car.find('Condition').text),
                'Odometer': int(car.find('Odometer').text),
                'MMR': int(car.find('MMR').text),
                'Year': int(car.find('./Specifications/Year').text),
                'Make': car.find('./Specifications/Make').text,
                'Model': car.find('./Specifications/Model').text,
                'Trim': car.find('./Specifications/Trim').text,
                'Body': car.find('./Specifications/Body').text,
                'Transmission': car.find('./Specifications/Transmission').text,
                'Color': car.find('./Specifications/Color').text,
                'Interior': car.find('./Specifications/Interior').text,
                'SellerName': car.find('./Seller/Name').text,
                'State': car.find('./Seller/State').text.strip(),
                'City': "Unknown",  # Add a default or parse if available
                'Latitude': float(car.find('./Seller/State/Coordinates/Latitude').text),
                'Longitude': float(car.find('./Seller/State/Coordinates/Longitude').text),
                'SaleDate': car.find('./Seller/SaleDate').text,
                'SellingPrice': int(car.find('./Seller/SellingPrice').text)
            }
            save_to_database(car_data)
    except Exception as e:
        logger.error(f"Error parsing XML: {e}", exc_info=True)


def process_message(ch, method, properties, body):
    """Process incoming RabbitMQ messages."""
    try:
        logger.info("Received message from RabbitMQ.")
        parse_xml_and_save(body.decode('utf-8'))
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def main():
    """Main function to start the RabbitMQ worker."""
    try:
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PW)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBITMQ_HOST,
                                      port=RABBITMQ_PORT,
                                      credentials=credentials)
        )
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE_NAME)
        channel.basic_consume(queue=QUEUE_NAME,
                              on_message_callback=process_message,
                              auto_ack=False)
        logger.info("Worker is waiting for messages.")
        channel.start_consuming()
    except Exception as e:
        logger.error(f"Error in main worker loop: {e}", exc_info=True)


if __name__ == "__main__":
    main()