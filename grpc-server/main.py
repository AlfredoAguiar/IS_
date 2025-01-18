from concurrent import futures
import os
import grpc
import logging
import pg8000
import pika
import xml.etree.ElementTree as ET
from xmlLocalização.uniqueStates import uniqueStates
from xmlLocalização.get_localização_states import StateCoordinatesUpdater
from xmlLocalização.loc_states import XMLLocationUpdater
from xmlGeneration.csv_to_xml_converter_cars import CSVtoXMLConverter
from xmlValidate.validate_xml import validate_xml
import server_services_pb2_grpc
import server_services_pb2
from settings import GRPC_SERVER_PORT, MAX_WORKERS, MEDIA_PATH, DBNAME, DBUSERNAME, DBPASSWORD, DBHOST, DBPORT

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "user")
RABBITMQ_PW = os.getenv("RABBITMQ_PW", "password")

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
            # Read and execute the SQL for table creation
            sql_file_path = 'createTablesCar.sql'
            with open(sql_file_path, 'r') as file:
                sql_queries = file.read()
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
            uniqueStates(xml_file_path, xml_US_path)
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
            coordinates_updater = StateCoordinatesUpdater(
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

class CarService(server_services_pb2_grpc.CarServiceServicer):

    def extract_car_data(self, xml_file_path):
        car_data = []
        try:
            tree = ET.parse(xml_file_path)
            root = tree.getroot()

            for car_elem in root.findall('Car'):
                vin = car_elem.find('VIN').text
                condition = car_elem.find('Condition').text
                odometer = car_elem.find('Odometer').text
                mmr = car_elem.find('MMR').text

                # Extracting the Specifications from the <Specifications> element
                specifications_elem = car_elem.find('Specifications')
                specifications = server_services_pb2.Specifications(
                    year=int(specifications_elem.find('Year').text),
                    make=specifications_elem.find('Make').text,
                    model=specifications_elem.find('Model').text,
                    trim=specifications_elem.find('Trim').text,
                    body=specifications_elem.find('Body').text,
                    transmission=specifications_elem.find('Transmission').text,
                    color=specifications_elem.find('Color').text,
                    interior=specifications_elem.find('Interior').text,
                )

                # Extracting Seller information
                seller_elem = car_elem.find('Seller')
                seller_name = seller_elem.find('Name').text
                seller_state = seller_elem.find('State').text

                # Extracting Coordinates from <State> inside <Seller>
                latitude = float(seller_elem.find('./State/Coordinates/Latitude').text)
                longitude = float(seller_elem.find('./State/Coordinates/Longitude').text)

                # Extracting Sale Date and Selling Price
                sale_date = seller_elem.find('SaleDate').text
                selling_price = int(seller_elem.find('SellingPrice').text)

                # Constructing the Car message with the extracted data
                car = server_services_pb2.Car(
                    vin=vin,
                    condition=int(condition),
                    odometer=int(odometer),
                    mmr=int(mmr),
                    specifications=specifications,
                    seller_name=seller_name,
                    seller_state=seller_state,
                    seller_coordinates=server_services_pb2.Coordinates(
                        latitude=latitude,
                        longitude=longitude,
                    ),
                    sale_date=sale_date,
                    selling_price=selling_price
                )

                car_data.append(car)

            return car_data
        except Exception as e:
            logger.error(f"Error extracting car data: {str(e)}", exc_info=True)
            return []

    def process_file(self, file_path, context):
        return self.extract_car_data(file_path)

    def GetAllCars(self, request, context):
        try:
            cars = self.process_file(os.path.join(MEDIA_PATH, ".csv.xmlFinal"), context)
            return server_services_pb2.GetAllCarsResponse(cars=cars)
        except Exception as e:
            context.set_details(f"Error fetching cars: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return server_services_pb2.GetAllCarsResponse()

    def GetCarsByMakeModel(self, request, context):
        try:
            cars = self.process_file(os.path.join(MEDIA_PATH, ".csv.xmlFinal"), context)
            filtered_cars = [car for car in cars if
                             car.specifications.make == request.make and car.specifications.model == request.model]
            return server_services_pb2.GetCarsByMakeModelResponse(cars=filtered_cars)
        except Exception as e:
            context.set_details(f"Error fetching cars: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return server_services_pb2.GetCarsByMakeModelResponse()



    def GetCarsByPriceRange(self, request, context):
        try:
            cars = self.process_file(os.path.join(MEDIA_PATH, ".csv.xmlFinal"), context)
            filtered_cars = [car for car in cars if request.min_price <= car.selling_price <= request.max_price]
            return server_services_pb2.GetCarsByPriceRangeResponse(cars=filtered_cars)
        except Exception as e:
            context.set_details(f"Error fetching cars: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return server_services_pb2.GetCarsByPriceRangeResponse()

    def GetCarsByYearCondition(self, request, context):
        try:
            cars = self.process_file(os.path.join(MEDIA_PATH, ".csv.xmlFinal"), context)
            filtered_cars = [car for car in cars if
                             car.specifications.year == request.year and car.condition == request.condition]
            return server_services_pb2.GetCarsByYearConditionResponse(cars=filtered_cars)
        except Exception as e:
            context.set_details(f"Error fetching cars: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return server_services_pb2.GetCarsByYearConditionResponse()

class CarService_db(server_services_pb2_grpc.CarServiceDatabaseServicer):
    def __init__(self):
        # Initialize database connection parameters
        self.db_params = {
            'user': DBUSERNAME,
            'password': DBPASSWORD,
            'host': DBHOST,
            'port': DBPORT,
            'database': DBNAME
        }

    def establish_db_connection(self):
        try:
            # Connect to the PostgreSQL database
            conn = pg8000.connect(**self.db_params)
            cursor = conn.cursor()
            return conn, cursor
        except Exception as e:
            raise Exception(f"Database connection error: {str(e)}")

    def GetAllCars(self, request, context):
        try:
            conn, cursor = self.establish_db_connection()

            # Fetch all cars along with specifications, sellers, and locations
            cursor.execute("""
                SELECT 
                    c.VIN, c.Condition, c.Odometer, c.MMR,
                    s.Year, s.Make, s.Model, s.Trim, s.Body, s.Transmission,
                    sl.Name, sl.State, sl.SaleDate, sl.SellingPrice,
                    l.City, l.Latitude, l.Longitude
                FROM Cars c
                LEFT JOIN Specifications s ON c.VIN = s.VIN
                LEFT JOIN Sellers sl ON c.VIN = sl.VIN
                LEFT JOIN Locations l ON c.VIN = l.VIN
            """)
            rows = cursor.fetchall()

            # Create a dictionary to store cars by VIN to avoid duplication
            cars_dict = {}

            for row in rows:
                vin = row[0]
                specifications = server_services_pb2.Specifications(
                    year=row[4] if row[4] is not None else 0,
                    make=row[5] if row[5] else "",
                    model=row[6] if row[6] else "",
                    trim=row[7] if row[7] else "",
                    body=row[8] if row[8] else "",
                    transmission=row[9] if row[9] else ""
                ) if row[4] is not None else None


                location = server_services_pb2.Coordinates(
                    latitude=row[15] if row[15] is not None else 0.0,
                    longitude=row[16] if row[16] is not None else 0.0
                ) if row[14] else None


                if vin not in cars_dict:
                    cars_dict[vin] = server_services_pb2.Car(
                        vin=vin,  # VIN
                        condition=row[1],  # Condition
                        odometer=row[2],  # Odometer
                        mmr=row[3] if row[3] is not None else 0,
                        seller_name=row[10] if row[10] else "",
                        seller_state=row[11] if row[11] else "",
                        sale_date=row[12] if row[12] else "",
                        selling_price=row[13] if row[13] is not None else 0,
                        specifications=specifications,
                        seller_coordinates=location
                    )
                else:
                    # Update existing car details if necessary
                    car = cars_dict[vin]
                    # In case seller data or location was missing for some rows
                    if not car.seller_name and row[10]:
                        car.seller_name = row[10]
                    if not car.seller_state and row[11]:
                        car.seller_state = row[11]
                    if not car.sale_date and row[12]:
                        car.sale_date = row[12]
                    if car.selling_price == 0 and row[13]:
                        car.selling_price = row[13]
                    if car.seller_coordinates == server_services_pb2.Coordinates() and location:
                        car.seller_coordinates = location
                    if not car.specifications:
                        car.specifications = specifications

            # Prepare the response
            cars = list(cars_dict.values())

            conn.close()
            return server_services_pb2.GetAllCarsResponse(cars=cars)

        except Exception as e:
            context.set_details(f"Error fetching cars: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return server_services_pb2.GetAllCarsResponse()

    def GetCarByVin(self, request, context):
        try:
            # Validate VIN input
            if not request.vin or len(request.vin) != 17:
                raise ValueError("VIN must be a 17-character string.")

            conn, cursor = self.establish_db_connection()

            # Fetch car details by VIN along with specifications, sellers, and locations
            cursor.execute("""
                SELECT 
                    c.VIN, c.Condition, c.Odometer, c.MMR,
                    s.Year, s.Make, s.Model, s.Trim, s.Body, s.Transmission,
                    sl.Name, sl.State, sl.SaleDate, sl.SellingPrice,
                    l.City, l.Latitude, l.Longitude
                FROM Cars c
                LEFT JOIN Specifications s ON c.VIN = s.VIN
                LEFT JOIN Sellers sl ON c.VIN = sl.VIN
                LEFT JOIN Locations l ON c.VIN = l.VIN
                WHERE c.VIN = %s
            """, (request.vin,))

            row = cursor.fetchone()

            if row is None:
                context.set_details(f"No car found with VIN {request.vin}")
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return server_services_pb2.GetCarByVinResponse()  # Return empty response if no car found

            # Create the specifications object (if it exists)
            specifications = server_services_pb2.Specifications(
                year=row[4] if row[4] is not None else 0,
                make=row[5] if row[5] else "",
                model=row[6] if row[6] else "",
                trim=row[7] if row[7] else "",
                body=row[8] if row[8] else "",
                transmission=row[9] if row[9] else ""
            ) if row[4] is not None else None

            # Create the location object (if it exists)
            location = server_services_pb2.Coordinates(
                latitude=row[15] if row[15] is not None else 0.0,
                longitude=row[16] if row[16] is not None else 0.0
            ) if row[14] else None

            # Create the car object
            car = server_services_pb2.Car(
                vin=row[0],  # VIN
                condition=row[1],  # Condition
                odometer=row[2],  # Odometer
                mmr=row[3] if row[3] is not None else 0,
                seller_name=row[10] if row[10] else "",
                seller_state=row[11] if row[11] else "",
                sale_date=row[12] if row[12] else "",
                selling_price=row[13] if row[13] is not None else 0,
                specifications=specifications,
                seller_coordinates=location
            )

            conn.close()

            # Return the car details in the response
            return server_services_pb2.GetCarByVinResponse(car=car)

        except Exception as e:
            logger.error(f"Error fetching car by VIN: {str(e)}")
            context.set_details(f"Error fetching car by VIN: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return server_services_pb2.GetCarByVinResponse()

    def UpdateCar(self, request, context):
        try:
            # Validate VIN (must be a 17-character string)
            if not request.vin or len(request.vin) != 17:
                raise ValueError("VIN must be a 17-character string.")

            # Establish database connection
            conn, cursor = self.establish_db_connection()

            # Update Cars table
            cursor.execute("""
                UPDATE Cars SET
                    Condition = %s,
                    Odometer = %s,
                    Color = %s,
                    Interior = %s,
                    MMR = %s
                WHERE VIN = %s
            """, (
                request.condition,
                request.odometer,
                request.color or "",  # Default to empty string if color is None
                request.interior or "",  # Default to empty string if interior is None
                request.mmr,
                request.vin
            ))

            # Update Specifications table
            cursor.execute("""
                UPDATE Specifications SET
                    Year = %s,
                    Make = %s,
                    Model = %s,
                    Trim = %s,
                    Body = %s,
                    Transmission = %s
                WHERE VIN = %s
            """, (
                request.specifications.year,
                request.specifications.make,
                request.specifications.model,
                request.specifications.trim,
                request.specifications.body,
                request.specifications.transmission,
                request.vin
            ))

            # Update Sellers table
            cursor.execute("""
                UPDATE Sellers SET
                    Name = %s,
                    State = %s,
                    SaleDate = %s,
                    SellingPrice = %s
                WHERE VIN = %s
            """, (
                request.seller_name,
                request.seller_state,
                request.sale_date,
                request.selling_price,
                request.vin
            ))

            # Update Locations table
            cursor.execute("""
                UPDATE Locations SET
                    City = %s,
                    Latitude = %s,
                    Longitude = %s
                WHERE VIN = %s
            """, (
                request.city,
                request.latitude,
                request.longitude,
                request.vin
            ))

            # Commit the transaction
            conn.commit()
            conn.close()

            # Return success response
            return server_services_pb2.UpdateCarResponse(success=True, message="Car updated successfully.")

        except Exception as e:
            # Log the error and return failure response
            logger.error(f"Error updating car: {str(e)}")
            context.set_details(f"Error updating car: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return server_services_pb2.UpdateCarResponse(success=False, message=str(e))
    def DeleteCar(self, request, context):
        try:
            conn, cursor = self.establish_db_connection()

            # Prepare the delete SQL statement
            cursor.execute("DELETE FROM Cars WHERE VIN = %s", (request.vin,))

            # Commit the transaction
            conn.commit()
            conn.close()

            return server_services_pb2.DeleteCarResponse(success=True, message="Car deleted successfully.")
        except Exception as e:
            context.set_details(f"Error deleting car: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return server_services_pb2.DeleteCarResponse(success=False, message=str(e))
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=MAX_WORKERS))

    server_services_pb2_grpc.add_CarServiceServicer_to_server(CarService(), server)
    server_services_pb2_grpc.add_SendFileServiceServicer_to_server(SendFileService(), server)
    server_services_pb2_grpc.add_CarServiceDatabaseServicer_to_server(CarService_db(), server)
    server.add_insecure_port(f'[::]:{GRPC_SERVER_PORT}')
    server.start()

    logger.info(f"gRPC Server started on port {GRPC_SERVER_PORT}")
    server.wait_for_termination()


if __name__ == '__main__':
    serve()