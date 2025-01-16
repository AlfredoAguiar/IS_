from concurrent import futures
import os
import grpc
import logging
import pg8000
from xmlGeneration.csv_to_xml_converter_cars import CSVtoXMLConverter
import server_services_pb2_grpc
import server_services_pb2
from settings import GRPC_SERVER_PORT, MAX_WORKERS, MEDIA_PATH, DBNAME, DBUSERNAME, DBPASSWORD, DBHOST, DBPORT
import pika
from xmlLocalização.uniqueStates import uniqueStates
from xmlLocalização.get_localização_states import StateCoordinatesUpdater
from xmlLocalização.loc_states import XMLLocationUpdater

# RabbitMQ Configuration
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "user")
RABBITMQ_PW = os.getenv("RABBITMQ_PW", "password")

# Configure logging
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger("FileService")

class SendFileService(server_services_pb2_grpc.SendFileServiceServicer):
    def SendFile(self, request, context):
        os.makedirs(MEDIA_PATH, exist_ok=True)
        csv_file_path = os.path.join(MEDIA_PATH, request.file_name + ".csvtest")
        xml_file_path = os.path.join(MEDIA_PATH, request.file_name + ".xmltest")

        # Save the received file as .csvtest
        ficheiro_em_bytes = request.file
        with open(csv_file_path, 'wb') as f:
            f.write(ficheiro_em_bytes)
        logger.info(f"CSV file saved at {csv_file_path}")

        # Establish Connection to PostgreSQL
        try:
            conn = pg8000.connect(
                user=DBUSERNAME,
                password=DBPASSWORD,
                host=DBHOST,
                port=DBPORT,
                database=DBNAME
            )
            cursor = conn.cursor()

           # SQL queries to create tables
            create_cars_table = """
                CREATE TABLE IF NOT EXISTS Cars (
                    VIN VARCHAR(17) PRIMARY KEY,
                    Condition INT,
                    Odometer INT,
                    Color VARCHAR(50),
                    Interior VARCHAR(50),
                    MMR INT
                );
            """
            create_specifications_table = """
                CREATE TABLE IF NOT EXISTS Specifications (
                    SpecID SERIAL PRIMARY KEY,
                    VIN VARCHAR(17) UNIQUE,
                    Year INT,
                    Make VARCHAR(50),
                    Model VARCHAR(50),
                    Trim VARCHAR(50),
                    Body VARCHAR(50),
                    Transmission VARCHAR(50),
                    FOREIGN KEY (VIN) REFERENCES Cars(VIN) ON DELETE CASCADE
                );
            """
            create_sellers_table = """
                CREATE TABLE IF NOT EXISTS Sellers (
                    SellerID SERIAL PRIMARY KEY,
                    VIN VARCHAR(17),
                    Name VARCHAR(255),
                    State VARCHAR(10),
                    SaleDate VARCHAR(255),
                    SellingPrice INT,
                    FOREIGN KEY (VIN) REFERENCES Cars(VIN) ON DELETE CASCADE
                );
            """
            create_locations_table = """
                CREATE TABLE IF NOT EXISTS Locations (
                    LocationID SERIAL PRIMARY KEY,
                    VIN VARCHAR(17),
                    City VARCHAR(100),
                    Latitude DECIMAL(9, 7),
                    Longitude DECIMAL(10, 7),
                    FOREIGN KEY (VIN) REFERENCES Cars(VIN) ON DELETE CASCADE
                );
            """

            # Execute the SQL queries to create tables
            cursor.execute(create_cars_table)
            cursor.execute(create_specifications_table)
            cursor.execute(create_sellers_table)
            cursor.execute(create_locations_table)
            conn.commit()

            cursor.execute(create_cars_table)

            cursor.execute(create_specifications_table)

            cursor.execute(create_sellers_table)

            cursor.execute(create_locations_table)

            conn.commit()


        except Exception as e:

            logger.error(f"Database Error: {str(e)}", exc_info=True)

            context.set_details(f"Database Error: {str(e)}")

            context.set_code(grpc.StatusCode.INTERNAL)

            return server_services_pb2.SendFileResponseBody(success=False)

            # Convert the CSV file to XML

        try:

            # Initialize the CSVtoXMLConverter with paths

            converter = CSVtoXMLConverter(csv_file_path, xml_file_path)

            converter.save_to_file()

            logger.info(f"XML file generated and saved at {xml_file_path}")

        except Exception as e:

            logger.error(f"CSV to XML Conversion Error: {str(e)}", exc_info=True)

            context.set_details(f"CSV to XML Conversion Error: {str(e)}")

            context.set_code(grpc.StatusCode.INTERNAL)

            return server_services_pb2.SendFileResponseBody(success=False)

            # Return success response

        return server_services_pb2.SendFileResponseBody(

            success=True,

            message=f"File processed successfully. XML generated at {xml_file_path}"

        )
    
    def SendFileChunks(self, request_iterator, context):
        try:
            os.makedirs(MEDIA_PATH, exist_ok=True)
            file_name = None
            file_chunks = []

            # Receber os chunks e combiná-los em um único arquivo
            for chunk in request_iterator:
                if not file_name:
                    file_name = chunk.file_name
                file_chunks.append(chunk.data)

            file_content = b"".join(file_chunks)
            csv_file_path = os.path.join(MEDIA_PATH, file_name + ".csvtest")
            xml_file_path = os.path.join(MEDIA_PATH, file_name + ".xmltest")
            xml_US_path = os.path.join(MEDIA_PATH, file_name + ".xmluniquestate")
            xml_Cord_path = os.path.join(MEDIA_PATH, file_name + ".xmlCord")
            xml_Final = os.path.join(MEDIA_PATH, file_name + ".xmlFinal")

            # Salvar o arquivo CSV final
            with open(csv_file_path, "wb") as f:
                f.write(file_content)
            logger.info(f"CSV file saved at {csv_file_path}")

            # Estabelecer conexão com PostgreSQL e criar tabelas
            try:
                conn = pg8000.connect(
                    user=DBUSERNAME,
                    password=DBPASSWORD,
                    host=DBHOST,
                    port=DBPORT,
                    database=DBNAME
                )
                cursor = conn.cursor()

                create_tables_queries = [
                    """
                    CREATE TABLE IF NOT EXISTS Cars (
                        VIN VARCHAR(17) PRIMARY KEY,
                        Condition INT,
                        Odometer INT,
                        Color VARCHAR(50),
                        Interior VARCHAR(50),
                        MMR INT
                    );
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS Specifications (
                        SpecID SERIAL PRIMARY KEY,
                        VIN VARCHAR(17) NOT NULL,
                        Year INT,
                        Make VARCHAR(50),
                        Model VARCHAR(50),
                        Trim VARCHAR(50),
                        Body VARCHAR(50),
                        Transmission VARCHAR(50),
                        UNIQUE (VIN), -- Adds a unique constraint to VIN
                        FOREIGN KEY (VIN) REFERENCES Cars(VIN) 
                    );
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS Sellers (
                        SellerID SERIAL PRIMARY KEY,
                        VIN VARCHAR(17) NOT NULL,
                        Name VARCHAR(255),
                        State VARCHAR(10),
                        SaleDate VARCHAR(255),
                        SellingPrice INT,
                        UNIQUE (VIN), -- Adds a unique constraint to VIN
                        FOREIGN KEY (VIN) REFERENCES Cars(VIN)
                    );
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS Locations (
                        LocationID SERIAL PRIMARY KEY,
                        VIN VARCHAR(17) NOT NULL,
                        City VARCHAR(100),
                        Latitude DECIMAL(9, 7),
                        Longitude DECIMAL(10, 7),
                        UNIQUE (VIN), -- Adds a unique constraint to VIN
                        FOREIGN KEY (VIN) REFERENCES Cars(VIN)
                    );
                    """
                ]

                for query in create_tables_queries:
                    cursor.execute(query)
                conn.commit()
                logger.info("Database tables ensured to exist.")

            except Exception as e:
                logger.error(f"Database Error: {str(e)}", exc_info=True)
                context.set_details(f"Database Error: {str(e)}")
                context.set_code(grpc.StatusCode.INTERNAL)
                return server_services_pb2.SendFileChunksResponse(success=False)

            # Converter CSV para XML
            try:
                converter = CSVtoXMLConverter(csv_file_path, xml_file_path)
                converter.save_to_file()
                logger.info(f"XML file generated and saved at {xml_file_path}")
            except Exception as e:
                logger.error(f"CSV to XML Conversion Error: {str(e)}", exc_info=True)
                context.set_details(f"CSV to XML Conversion Error: {str(e)}")
                context.set_code(grpc.StatusCode.INTERNAL)
                return server_services_pb2.SendFileChunksResponse(success=False)

            # Processar estados únicos no XML
            try:
                uniqueStates(xml_file_path, xml_US_path)
                logger.info(f"Unique states processed and saved in XML at {xml_US_path}")
            except Exception as e:
                logger.error(f"Error processing unique states in XML: {str(e)}", exc_info=True)
                context.set_details(f"Error processing unique states in XML: {str(e)}")
                context.set_code(grpc.StatusCode.INTERNAL)
                return server_services_pb2.SendFileChunksResponse(success=False)

            # Atualizar dados de localização no XML
            try:
                location_updater = XMLLocationUpdater(
                    cars_file=xml_file_path,
                    coordinates_file=xml_US_path,
                    output_file=xml_Cord_path
                )
                location_updater.update_locations()
                logger.info("Locations updated and saved in the XML file.")
            except Exception as e:
                logger.error(f"Error adding location data or saving XML: {str(e)}", exc_info=True)
                context.set_details(f"Error adding location data or saving XML: {str(e)}")
                context.set_code(grpc.StatusCode.INTERNAL)
                return server_services_pb2.SendFileChunksResponse(success=False)

            # Atualizar coordenadas no XML final
            try:
                coordinates_updater = StateCoordinatesUpdater(
                    input_path=xml_file_path,
                    output_path=xml_Final
                )
                coordinates_updater.update_xml_with_coordinates()
                logger.info("Final XML file generated with updated coordinates.")
            except Exception as e:
                logger.error(f"Error updating coordinates in XML: {str(e)}", exc_info=True)
                context.set_details(f"Error updating coordinates in XML: {str(e)}")
                context.set_code(grpc.StatusCode.INTERNAL)
                return server_services_pb2.SendFileChunksResponse(success=False)

            # Conectar ao RabbitMQ e enviar o XML final
            try:
                rabbit_connection = pika.BlockingConnection(
                    pika.ConnectionParameters(
                        host=RABBITMQ_HOST,
                        port=RABBITMQ_PORT,
                        credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PW)
                    )
                )
                rabbit_channel = rabbit_connection.channel()
                rabbit_channel.queue_declare(queue='xml_final')

                # Ler o conteúdo do arquivo XML final
                with open(xml_Final, "rb") as f:
                    xml_content = f.read()

                # Enviar o XML final ao RabbitMQ
                rabbit_channel.basic_publish(
                    exchange='',
                    routing_key='xml_final',
                    body=xml_content
                )
                logger.info("XML Final sent to RabbitMQ queue 'xml_final'.")

                rabbit_connection.close()
            except Exception as e:
                logger.error(f"RabbitMQ Error: {str(e)}", exc_info=True)
                context.set_details(f"RabbitMQ Error: {str(e)}")
                context.set_code(grpc.StatusCode.INTERNAL)
                return server_services_pb2.SendFileChunksResponse(success=False)

            logger.info("All operations completed successfully.")
            return server_services_pb2.SendFileChunksResponse(
                success=True,
                message="File processed and XML sent to RabbitMQ successfully."
            )

        except Exception as e:
            logger.error(f"General Error: {str(e)}", exc_info=True)
            context.set_details(f"General Error: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return server_services_pb2.SendFileChunksResponse(success=False)
    



def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=MAX_WORKERS))
    server_services_pb2_grpc.add_SendFileServiceServicer_to_server(SendFileService(), server)
    server.add_insecure_port(f'[::]:{GRPC_SERVER_PORT}')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
