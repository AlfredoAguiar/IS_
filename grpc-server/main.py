from concurrent import futures
import os
import grpc
import logging
import pg8000
from xmlGeneration.csv_to_xml_converter_cars import CSVtoXMLConverter
import server_services_pb2_grpc
import server_services_pb2
from settings import GRPC_SERVER_PORT, MAX_WORKERS, MEDIA_PATH, DBNAME, DBUSERNAME, DBPASSWORD, DBHOST, DBPORT


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
                VIN VARCHAR(17),
                Year INT,
                Make VARCHAR(50),
                Model VARCHAR(50),
                Trim VARCHAR(50),
                Body VARCHAR(50),
                Transmission VARCHAR(50),
                FOREIGN KEY (VIN) REFERENCES Cars(VIN)
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
                FOREIGN KEY (VIN) REFERENCES Cars(VIN)
            );
            """
        create_locations_table = """
            CREATE TABLE IF NOT EXISTS Locations (
                LocationID SERIAL PRIMARY KEY,
                VIN VARCHAR(17),
                City VARCHAR(100),
                Latitude DECIMAL(9, 7),
                Longitude DECIMAL(10, 7),
                FOREIGN KEY (VIN) REFERENCES Cars(VIN)
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
            file_chunks = []  # Armazenar todos os chunks na memória

            for chunk in request_iterator:
                if not file_name:
                    file_name = chunk.file_name
                # Coletar os dados do arquivo
                file_chunks.append(chunk.data)

            # Combinar todos os chunks em um único objeto de bytes
            file_content = b"".join(file_chunks)
            file_path = os.path.join(MEDIA_PATH, file_name)

            # Escrever os dados coletados no arquivo no final
            with open(file_path, "wb") as f:
                f.write(file_content)
            logger.info(f"File {file_name} saved successfully at {MEDIA_PATH}")

            return server_services_pb2.SendFileChunksResponse(success=True, message="File imported successfully")

        except Exception as e:
            logger.error(f"Error: {str(e)}", exc_info=True)
            return server_services_pb2.SendFileChunksResponse(success=False, message=str(e))


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=MAX_WORKERS))
    server_services_pb2_grpc.add_SendFileServiceServicer_to_server(SendFileService(), server)
    server.add_insecure_port(f'[::]:{GRPC_SERVER_PORT}')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
