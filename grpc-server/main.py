from concurrent import futures
import os
import grpc
import logging
import pg8000
from xmlLocalização.uniqueStates import uniqueStates
from xmlLocalização.get_localização_states import StateCoordinatesUpdater
from xmlLocalização.loc_states import XMLLocationUpdater
from xmlGeneration.csv_to_xml_converter_cars import CSVtoXMLConverter
from xmlValidate.validate_xml import validate_xml
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
        xml_US_path = os.path.join(MEDIA_PATH, request.file_name + ".xmluniquestate")
        xml_Cord_path = os.path.join(MEDIA_PATH, request.file_name + ".xmlCord")
        xml_Final = os.path.join(MEDIA_PATH, request.file_name + ".xmlFinal")
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
                    VIN VARCHAR(17),
                    Year INT,
                    Make VARCHAR(50),
                    Model VARCHAR(50),
                    Trim VARCHAR(50),
                    Body VARCHAR(50),
                    Transmission VARCHAR(50),
                    FOREIGN KEY (VIN) REFERENCES Cars(VIN)
                );
                """,
                """
                CREATE TABLE IF NOT EXISTS Sellers (
                    SellerID SERIAL PRIMARY KEY,
                    VIN VARCHAR(17),
                    Name VARCHAR(255),
                    State VARCHAR(10),
                    SaleDate VARCHAR(255),
                    SellingPrice INT,
                    FOREIGN KEY (VIN) REFERENCES Cars(VIN)
                );
                """,
                """
                CREATE TABLE IF NOT EXISTS Locations (
                    LocationID SERIAL PRIMARY KEY,
                    VIN VARCHAR(17),
                    City VARCHAR(100),
                    Latitude DECIMAL(9, 7),
                    Longitude DECIMAL(10, 7),
                    FOREIGN KEY (VIN) REFERENCES Cars(VIN)
                );
                """
            ]

            # Execute all table creation queries
            for query in create_tables_queries:
                cursor.execute(query)
            conn.commit()

            logger.info("Database tables ensured to exist.")

        except Exception as e:
            logger.error(f"Database Error: {str(e)}", exc_info=True)
            context.set_details(f"Database Error: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return server_services_pb2.SendFileResponseBody(success=False)

        # Convert the CSV file to XML
        try:
            converter = CSVtoXMLConverter(csv_file_path, xml_file_path)
            converter.save_to_file()
            logger.info(f"XML file generated and saved at {xml_file_path}")
        except Exception as e:
            logger.error(f"CSV to XML Conversion Error: {str(e)}", exc_info=True)
            context.set_details(f"CSV to XML Conversion Error: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return server_services_pb2.SendFileResponseBody(success=False)

        # Process unique states in the generated XML
        try:

            uniqueStates(xml_file_path, xml_US_path)
            logger.info(f"Unique states processed and saved in XML at {xml_US_path}")
        except Exception as e:
            logger.error(f"Error processing unique states in XML: {str(e)}", exc_info=True)
            context.set_details(f"Error processing unique states in XML: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return server_services_pb2.SendFileResponseBody(success=False)

        try:
            # Instantiate the XMLLocationUpdater class
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
            return server_services_pb2.SendFileResponseBody(success=False)

        try:

            coordinates_updater = StateCoordinatesUpdater(
                input_path=xml_file_path,
                output_path=xml_Final
            )

            coordinates_updater.update_xml_with_coordinates()
            logger.info("Locations updated and saved in the XML file.")

        except Exception as e:
            logger.error(f"Error adding location data or saving XML: {str(e)}", exc_info=True)
            context.set_details(f"Error adding location data or saving XML: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return server_services_pb2.SendFileResponseBody(success=False)

            # Validate the generated XML file
        try:
                validation_result = validate_xml(xml_Final)
                logger.info(f"XML Validation Result: {validation_result}")
                if "not valid" in validation_result:
                    context.set_details(validation_result)
                    context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                    return server_services_pb2.SendFileResponse(success=False)
        except Exception as e:
                logger.error(f"XML Validation Error: {str(e)}", exc_info=True)
                context.set_details(f"XML Validation Error: {str(e)}")
                context.set_code(grpc.StatusCode.INTERNAL)
                return server_services_pb2.SendFileResponse(success=False)

        logger.info("All operations completed successfully.")
        return server_services_pb2.SendFileResponseBody(success=True, message="File processed and XML generated "
                                                                              "successfully.")



def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=MAX_WORKERS))
    server_services_pb2_grpc.add_SendFileServiceServicer_to_server(SendFileService(), server)
    server.add_insecure_port(f'[::]:{GRPC_SERVER_PORT}')
    server.start()
    logger.info(f"gRPC Server started on port {GRPC_SERVER_PORT}")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
