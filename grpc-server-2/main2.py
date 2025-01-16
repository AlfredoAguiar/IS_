from concurrent import futures
import os
import grpc
import logging
import pg8000
from xmlLocalização.uniqueCities import uniqueCities
from xmlLocalização.CityCoordinatesUpdater import CityCoordinatesUpdater
from xmlLocalização.loc_states import XMLLocationUpdater
from xmlGeneration.csv_to_xml_converter_Temp import CSVtoXMLConverter
from xmlValidate.validate_xml import validate_xml
import server_services_pb2_grpc
import server_services_pb2
from settings import GRPC_SERVER_PORT, MAX_WORKERS, MEDIA_PATH, DBNAME, DBUSERNAME, DBPASSWORD, DBHOST, DBPORT
from datetime import datetime
from xml.etree import ElementTree as ET

# Configure logging
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger("FileService")

class SendFileService(server_services_pb2_grpc.SendFileServiceServicer):
    def save_csv_file(self, file_bytes, file_path):
        try:
            with open(file_path, 'wb') as f:
                f.write(file_bytes)
            logger.info(f"CSV file saved at {file_path}")
        except Exception as e:
            logger.error(f"Error saving CSV file: {str(e)}", exc_info=True)
            raise e

    def establish_db_connection(self):
        try:
            conn = pg8000.connect(
                user=DBUSERNAME,
                password=DBPASSWORD,
                host=DBHOST,
                port=DBPORT,
                database=DBNAME
            )
            cursor = conn.cursor()

            # Read the SQL file containing the table creation queries
            sql_file_path = 'createTablesTemp.sql'
            with open(sql_file_path, 'r') as file:
                sql_queries = file.read()

            # Execute the SQL queries
            cursor.execute(sql_queries)
            conn.commit()

            logger.info("Database tables ensured to exist.")
        except Exception as e:
            logger.error(f"Database Error: {str(e)}", exc_info=True)
            raise e

    def convert_csv_to_xml(self, csv_file_path, xml_file_path):
        try:
            converter = CSVtoXMLConverter(csv_file_path, xml_file_path)
            converter.save_to_file()
            logger.info(f"XML file generated and saved at {xml_file_path}")
        except Exception as e:
            logger.error(f"CSV to XML Conversion Error: {str(e)}", exc_info=True)
            raise e

    def process_unique_states(self, xml_file_path, xml_US_path):
        try:
            uniqueCities(xml_file_path, xml_US_path)
            logger.info(f"Unique states processed and saved in XML at {xml_US_path}")
        except Exception as e:
            logger.error(f"Error processing unique states in XML: {str(e)}", exc_info=True)
            raise e

    def update_locations_in_xml(self, xml_file_path, xml_US_path, xml_Cord_path):
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
            raise e

    def update_coordinates_in_xml(self, xml_file_path, xml_Final):
        try:
            coordinates_updater = CityCoordinatesUpdater(
                input_path=xml_file_path,
                output_path=xml_Final
            )
            coordinates_updater.update_xml_with_coordinates()
            logger.info("Final XML file generated with updated coordinates.")
        except Exception as e:
            logger.error(f"Error updating coordinates in XML: {str(e)}", exc_info=True)
            raise e

    def validate_xml_file(self, xml_Final, context):
        try:
            validation_result = validate_xml(xml_Final)
            logger.info(f"XML Validation Result: {validation_result}")
            if "not valid" in validation_result:
                context.set_details(validation_result)
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                return False
            return True
        except Exception as e:
            logger.error(f"XML Validation Error: {str(e)}", exc_info=True)
            context.set_details(f"XML Validation Error: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return False

    def SendFile(self, request, context):
        os.makedirs(MEDIA_PATH, exist_ok=True)
        csv_file_path = os.path.join(MEDIA_PATH, request.file_name + ".csvtest")
        xml_file_path = os.path.join(MEDIA_PATH, request.file_name + ".xmltest")
        xml_US_path = os.path.join(MEDIA_PATH, request.file_name + ".xmluniquestate")
        xml_Cord_path = os.path.join(MEDIA_PATH, request.file_name + ".xmlCord")
        xml_Final = os.path.join(MEDIA_PATH, request.file_name + ".xmlFinal")

        try:
            # Save the received file as .csvtest
            self.save_csv_file(request.file, csv_file_path)

            # Establish DB connection
            self.establish_db_connection()

            # Convert CSV to XML
            self.convert_csv_to_xml(csv_file_path, xml_file_path)

            # Process unique states in the generated XML
            self.process_unique_states(xml_file_path, xml_US_path)

            # Update locations in the XML file
            self.update_locations_in_xml(xml_file_path, xml_US_path, xml_Cord_path)

            # Update coordinates in the XML file
            self.update_coordinates_in_xml(xml_file_path, xml_Final)

            # Validate the generated XML file
            if not self.validate_xml_file(xml_Final, context):
                return server_services_pb2.SendFileResponseBody(success=False)

        except Exception as e:
            logger.error(f"General Error: {str(e)}", exc_info=True)
            context.set_details(f"General Error: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return server_services_pb2.SendFileResponseBody(success=False)

        logger.info("All operations completed successfully.")
        return server_services_pb2.SendFileResponseBody(success=True, message="File processed and XML generated successfully.")

    def SendFileChunks(self, request_iterator, context):
        try:
            # Prepare paths and file chunks
            os.makedirs(MEDIA_PATH, exist_ok=True)
            file_name = None
            file_chunks = []

            # Receive chunks and combine them into a single file
            for chunk in request_iterator:
                if not file_name:
                    file_name = chunk.file_name  # Set file name once
                file_chunks.append(chunk.data)  # Append each chunk of file data

            file_content = b"".join(file_chunks)

            # Define file paths based on file name
            csv_file_path = os.path.join(MEDIA_PATH, file_name + ".csvtest")
            xml_file_path = os.path.join(MEDIA_PATH, file_name + ".xmltest")
            xml_US_path = os.path.join(MEDIA_PATH, file_name + ".xmluniquestate")
            xml_Cord_path = os.path.join(MEDIA_PATH, file_name + ".xmlCord")
            xml_Final = os.path.join(MEDIA_PATH, file_name + ".xmlFinal")

            # Save the received file content to a .csv file
            self.save_csv_file(file_content, csv_file_path)

            # Establish DB connection
            self.establish_db_connection()

            # Convert CSV to XML
            self.convert_csv_to_xml(csv_file_path, xml_file_path)

            # Process unique states in the generated XML
            self.process_unique_states(xml_file_path, xml_US_path)

            # Update locations in the XML file
            self.update_locations_in_xml(xml_file_path, xml_US_path, xml_Cord_path)

            # Update coordinates in the XML file
            self.update_coordinates_in_xml(xml_file_path, xml_Final)

            # Validate the generated XML file
            if not self.validate_xml_file(xml_Final, context):
                return server_services_pb2.SendFileChunksResponse(success=False)

            # Send the XML final file to RabbitMQ
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

                # Read the content of the final XML file
                with open(xml_Final, "rb") as f:
                    xml_content = f.read()

                # Send the XML to RabbitMQ queue 'xml_final'
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
class WeatherService(server_services_pb2_grpc.WeatherServiceServicer):
    def parse_weather_data_from_xml(self, xml_file_path):
        weather_data = []
        try:
            tree = ET.parse(xml_file_path)
            root = tree.getroot()

            # Traverse through <WeatherData> elements
            for record in root.findall('WeatherData'):
                region = record.find('Region').text
                country = record.find('Country').text
                state = record.find('State').text if record.find('State') is not None else ""
                city = record.find('City').text
                raw_date = record.find('Date').text
                try:

                    parsed_date = datetime.strptime(raw_date, "%m/%d/%Y").strftime("%Y-%m-%d")
                except ValueError:
                    logger.warning(f"Invalid date format in XML: {raw_date}")
                    continue

                avg_temperature = float(record.find('AvgTemperature').text)
                latitude = float(record.find('./Coordinates/Latitude').text)
                longitude = float(record.find('./Coordinates/Longitude').text)


                weather_data.append(server_services_pb2.WeatherData(
                    region=region,
                    country=country,
                    state=state,
                    city=city,
                    date=parsed_date,
                    avg_temperature=avg_temperature,
                    coordinates=server_services_pb2.Coordinates(latitude=latitude, longitude=longitude)
                ))
        except Exception as e:
            logger.error(f"Error parsing XML: {str(e)}", exc_info=True)
        return weather_data

    def GetWeatherByRegion(self, request, context):
        xml_file_path = os.path.join(MEDIA_PATH, ".csv.xmlFinal")
        weather_data = self.parse_weather_data_from_xml(xml_file_path)

        # Filter data by region
        filtered_data = [data for data in weather_data if data.region == request.region]

        if not filtered_data:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("No weather data found for the specified region.")
            return server_services_pb2.GetWeatherByRegionResponse(weather_data=[])

        return server_services_pb2.GetWeatherByRegionResponse(weather_data=filtered_data)

    def GetWeatherByLocation(self, request, context):
        xml_file_path = os.path.join(MEDIA_PATH, ".csv.xmlFinal")
        weather_data = self.parse_weather_data_from_xml(xml_file_path)

        # Find data by country and city
        for data in weather_data:
            if data.country == request.country and data.city == request.city:
                return server_services_pb2.GetWeatherByLocationResponse(weather_data=data)
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details("Weather data not found for the specified location.")
        return server_services_pb2.GetWeatherByLocationResponse()

    def GetWeatherByDateRange(self, request, context):
        xml_file_path = os.path.join(MEDIA_PATH, ".csv.xmlFinal")  # Adjust path if needed
        weather_data = self.parse_weather_data_from_xml(xml_file_path)

        try:
            # Parse start_date and end_date from the request
            start_date = datetime.strptime(request.start_date, "%Y-%m-%d")
            end_date = datetime.strptime(request.end_date, "%Y-%m-%d")
        except ValueError:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Invalid date format. Use YYYY-MM-DD.")
            return server_services_pb2.GetWeatherByDateRangeResponse()

        # Filter data by date range
        filtered_data = [
            data for data in weather_data
            if start_date <= datetime.strptime(data.date, "%Y-%m-%d") <= end_date
        ]

        if not filtered_data:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("No weather data found for the specified date range.")
            return server_services_pb2.GetWeatherByDateRangeResponse(weather_data=[])

        return server_services_pb2.GetWeatherByDateRangeResponse(weather_data=filtered_data)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=MAX_WORKERS))

    # Add SendFileService
    server_services_pb2_grpc.add_SendFileServiceServicer_to_server(SendFileService(), server)

    # Add WeatherService
    server_services_pb2_grpc.add_WeatherServiceServicer_to_server(WeatherService(), server)

    server.add_insecure_port(f'[::]:{GRPC_SERVER_PORT}')
    server.start()
    logger.info(f"gRPC Server started on port {GRPC_SERVER_PORT}")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
