from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..serializers.file_serializer import FileUploadSerializer
import grpc
from api.grpc_ import server_services_pb2 as server_services_pb2
from api.grpc_ import server_services_pb2_grpc as server_services_pb2_grpc
import os
from rest_api_server.settings import GRPC_PORT, GRPC_HOST
import logging

class FileUploadView(APIView):
    def post(self, request):
        serializer = FileUploadSerializer(data=request.data)

        if serializer.is_valid():
            file = serializer.validated_data['file']

            if not file:
                return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)
            o
            file_name, file_extension = os.path.splitext(file.name)

            file_content = file.read()

            channel = grpc.insecure_channel(f'{GRPC_HOST}:{GRPC_PORT}')
            stub = server_services_pb2_grpc.SendFileServiceStub(channel)

            grpc_request = server_services_pb2.SendFileRequestBody(
                file_name=file_name,
                file_mime=file_extension,
                file=file_content
            )

            try:
                stub.SendFile(grpc_request)

                return Response({
                    "file_name": file_name,
                    "file_extension": file_extension
                }, status=status.HTTP_201_CREATED)
            
            except grpc.RpcError as e:

                return Response({
                    "error": f"gRPC call failed: {e.details()}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class FileUploadChunksView(APIView):
    def post(self, request):
        serializer = FileUploadSerializer(data=request.data)

        if serializer.is_valid():
            file = serializer.validated_data['file']

            if not file:
                return Response(
                    {"error": "No file uploaded"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            channel = grpc.insecure_channel(f'{GRPC_HOST}:{GRPC_PORT}')
            stub = server_services_pb2_grpc.SendFileServiceStub(channel)

            def generate_file_chunks(file, file_name, chunk_size=(64 * 1024)):
                """
                Gera os chunks do arquivo para envio.
                """
                try:
                    while chunk := file.read(chunk_size):
                        yield server_services_pb2.SendFileChunksRequest(
                            data=chunk,
                            file_name=file_name
                        )
                except Exception as e:
                    print(f"Error reading file: {e}")
                    raise  # Propagar a exceção

            # Enviar os chunks do arquivo para o serviço gRPC
            try:
                response = stub.SendFileChunks(generate_file_chunks(file, file.name, (64 * 1024)))
                if response.success:
                    return Response(
                        {"file_name": file.name},
                        status=status.HTTP_201_CREATED
                    )
                return Response(
                    {"error": f"gRPC response error: {response.message}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            except grpc.RpcError as e:
                return Response(
                    {"error": f"gRPC call failed: {e.details()}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class GetAllCarsView(APIView):
        def get(self, request):

            channel = grpc.insecure_channel(f'{GRPC_HOST}:{GRPC_PORT}')
            stub = server_services_pb2_grpc.CarServiceStub(channel)

            try:
                response = stub.GetAllCars(server_services_pb2.GetAllCarsRequest())
                cars = [
                    {
                        "vin": car.vin,
                        "condition": car.condition,
                        "odometer": car.odometer,
                        "mmr": car.mmr,
                        "specifications": {
                            "year": car.specifications.year,
                            "make": car.specifications.make,
                            "model": car.specifications.model,
                            "trim": car.specifications.trim,
                            "body": car.specifications.body,
                            "transmission": car.specifications.transmission,
                            "color": car.specifications.color,
                            "interior": car.specifications.interior,
                        },
                        "seller_name": car.seller_name,
                        "seller_state": car.seller_state,
                        "seller_coordinates": {
                            "latitude": car.seller_coordinates.latitude,
                            "longitude": car.seller_coordinates.longitude,
                        },
                        "sale_date": car.sale_date,
                        "selling_price": car.selling_price,
                    }
                    for car in response.cars
                ]
                return Response(cars, status=status.HTTP_200_OK)
            except grpc.RpcError as e:
                return Response({"error": f"gRPC call failed: {e.details()}"},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetCarsByMakeModelView(APIView):
        def get(self, request):
            """
            Filters cars by make and model.
            """
            make = request.query_params.get("make")
            model = request.query_params.get("model")
            if not make or not model:
                return Response({"error": "Make and model are required."}, status=status.HTTP_400_BAD_REQUEST)

            channel = grpc.insecure_channel(f'{GRPC_HOST}:{GRPC_PORT}')
            stub = server_services_pb2_grpc.CarServiceStub(channel)

            try:
                response = stub.GetCarsByMakeModel(
                    server_services_pb2.GetCarsByMakeModelRequest(make=make, model=model)
                )
                cars = [
                    {
                        "vin": car.vin,
                        "condition": car.condition,
                        "odometer": car.odometer,
                        "mmr": car.mmr,
                        "specifications": {
                            "year": car.specifications.year,
                            "make": car.specifications.make,
                            "model": car.specifications.model,
                            "trim": car.specifications.trim,
                            "body": car.specifications.body,
                            "transmission": car.specifications.transmission,
                            "color": car.specifications.color,
                            "interior": car.specifications.interior,
                        },
                        "seller_name": car.seller_name,
                        "seller_state": car.seller_state,
                        "seller_coordinates": {
                            "latitude": car.seller_coordinates.latitude,
                            "longitude": car.seller_coordinates.longitude,
                        },
                        "sale_date": car.sale_date,
                        "selling_price": car.selling_price,
                    }
                    for car in response.cars
                ]
                return Response(cars, status=status.HTTP_200_OK)
            except grpc.RpcError as e:
                return Response({"error": f"gRPC call failed: {e.details()}"},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetCarsByPriceRangeView(APIView):
        def get(self, request):
            """
            Filters cars by price range.
            """
            min_price = request.query_params.get("min_price")
            max_price = request.query_params.get("max_price")

            if not min_price or not max_price:
                return Response({"error": "min_price and max_price are required."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                min_price = int(min_price)
                max_price = int(max_price)
            except ValueError:
                return Response({"error": "min_price and max_price must be integers."},
                                status=status.HTTP_400_BAD_REQUEST)

            channel = grpc.insecure_channel(f'{GRPC_HOST}:{GRPC_PORT}')
            stub = server_services_pb2_grpc.CarServiceStub(channel)

            try:
                response = stub.GetCarsByPriceRange(
                    server_services_pb2.GetCarsByPriceRangeRequest(min_price=min_price, max_price=max_price)
                )
                cars = [
                    {
                        "vin": car.vin,
                        "condition": car.condition,
                        "odometer": car.odometer,
                        "mmr": car.mmr,
                        "specifications": {
                            "year": car.specifications.year,
                            "make": car.specifications.make,
                            "model": car.specifications.model,
                            "trim": car.specifications.trim,
                            "body": car.specifications.body,
                            "transmission": car.specifications.transmission,
                            "color": car.specifications.color,
                            "interior": car.specifications.interior,
                        },
                        "seller_name": car.seller_name,
                        "seller_state": car.seller_state,
                        "seller_coordinates": {
                            "latitude": car.seller_coordinates.latitude,
                            "longitude": car.seller_coordinates.longitude,
                        },
                        "sale_date": car.sale_date,
                        "selling_price": car.selling_price,
                    }
                    for car in response.cars
                ]
                return Response(cars, status=status.HTTP_200_OK)
            except grpc.RpcError as e:
                return Response({"error": f"gRPC call failed: {e.details()}"},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetCarsByYearConditionView(APIView):
        def get(self, request):
            """
            Filters cars by year and condition.
            """
            year = request.query_params.get("year")
            condition = request.query_params.get("condition")

            if not year or not condition:
                return Response({"error": "year and condition are required."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                year = int(year)
                condition = int(condition)
            except ValueError:
                return Response({"error": "year and condition must be integers."}, status=status.HTTP_400_BAD_REQUEST)

            channel = grpc.insecure_channel(f'{GRPC_HOST}:{GRPC_PORT}')
            stub = server_services_pb2_grpc.CarServiceStub(channel)

            try:
                response = stub.GetCarsByYearCondition(
                    server_services_pb2.GetCarsByYearConditionRequest(year=year, condition=condition)
                )
                cars = [
                    {
                        "vin": car.vin,
                        "condition": car.condition,
                        "odometer": car.odometer,
                        "mmr": car.mmr,
                        "specifications": {
                            "year": car.specifications.year,
                            "make": car.specifications.make,
                            "model": car.specifications.model,
                            "trim": car.specifications.trim,
                            "body": car.specifications.body,
                            "transmission": car.specifications.transmission,
                            "color": car.specifications.color,
                            "interior": car.specifications.interior,
                        },
                        "seller_name": car.seller_name,
                        "seller_state": car.seller_state,
                        "seller_coordinates": {
                            "latitude": car.seller_coordinates.latitude,
                            "longitude": car.seller_coordinates.longitude,
                        },
                        "sale_date": car.sale_date,
                        "selling_price": car.selling_price,
                    }
                    for car in response.cars
                ]
                return Response(cars, status=status.HTTP_200_OK)
            except grpc.RpcError as e:
                return Response({"error": f"gRPC call failed: {e.details()}"},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetCarByVinView(APIView):
    def get(self, request):
        vin = request.query_params.get("vin")
        if not vin or len(vin) != 17:
            return Response({"error": "VIN must be a 17-character string."}, status=status.HTTP_400_BAD_REQUEST)

        # Connect to the gRPC service
        channel = grpc.insecure_channel(f'{GRPC_HOST}:{GRPC_PORT}')
        stub = server_services_pb2_grpc.CarServiceDatabaseStub(channel)

        try:
            # Send the request to gRPC service
            response = stub.GetCarByVin(server_services_pb2.GetCarByVinRequest(vin=vin))

            if not response.car:
                return Response({"error": "Car not found."}, status=status.HTTP_404_NOT_FOUND)

            # Extract the car details from the gRPC response
            car = {
                "vin": response.car.vin,
                "condition": response.car.condition,
                "odometer": response.car.odometer,
                "mmr": response.car.mmr,
                "specifications": {
                    "year": response.car.specifications.year,
                    "make": response.car.specifications.make,
                    "model": response.car.specifications.model,
                    "trim": response.car.specifications.trim,
                    "body": response.car.specifications.body,
                    "transmission": response.car.specifications.transmission,
                },
                "seller_name": response.car.seller_name,
                "seller_state": response.car.seller_state,
                "sale_date": response.car.sale_date,
                "selling_price": response.car.selling_price,
                "seller_coordinates": {
                    "latitude": response.car.seller_coordinates.latitude,
                    "longitude": response.car.seller_coordinates.longitude,
                }
            }

            return Response(car, status=status.HTTP_200_OK)

        except grpc.RpcError as e:
            return Response({"error": f"gRPC call failed: {e.details()}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateCarView(APIView):
    def put(self, request):
        vin = request.data.get("vin")

        # Validate VIN
        if not vin or len(vin) != 17:
            return Response({"error": "VIN must be a 17-character string."}, status=status.HTTP_400_BAD_REQUEST)

        # Prepare the data to send to the gRPC service for updating Seller information
        update_data = server_services_pb2.UpdateCarRequest(
            vin=vin,
            seller_name=request.data.get("seller_name"),
            seller_state=request.data.get("seller_state"),
            sale_date=request.data.get("sale_date"),
            selling_price=request.data.get("selling_price")
        )

        # Log the data being sent to the gRPC service for debugging
        logging.debug(f"Sending update data to gRPC: {update_data}")

        # Connect to the gRPC service
        channel = grpc.insecure_channel(f'{GRPC_HOST}:{GRPC_PORT}')
        stub = server_services_pb2_grpc.CarServiceDatabaseStub(channel)

        try:
            # Send the update request to the gRPC service
            response = stub.UpdateCar(update_data)

            # Log the response from the gRPC server
            logging.debug(f"gRPC Response: {response}")

            if response.success:
                return Response({"message": "Seller details updated successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": response.message}, status=status.HTTP_400_BAD_REQUEST)

        except grpc.RpcError as e:
            # Log the gRPC error details for debugging
            logging.error(f"gRPC call failed: {e.details()}")
            return Response({"error": f"gRPC call failed: {e.details()}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class DeleteCarView(APIView):
    def delete(self, request):
        vin = request.data.get("vin")


        # Connect to the gRPC service
        channel = grpc.insecure_channel(f'{GRPC_HOST}:{GRPC_PORT}')
        stub = server_services_pb2_grpc.CarServiceDatabaseStub(channel)

        try:
            # Send the delete request to the gRPC service
            response = stub.DeleteCar(server_services_pb2.DeleteCarRequest(vin=vin))

            if response.success:
                return Response({"message": "Car deleted successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": response.message}, status=status.HTTP_400_BAD_REQUEST)

        except grpc.RpcError as e:
            return Response({"error": f"gRPC call failed: {e.details()}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetAllCarsView_2(APIView):
    def get(self, request):
        channel = grpc.insecure_channel(f'{GRPC_HOST}:{GRPC_PORT}')
        stub = server_services_pb2_grpc.CarServiceDatabaseStub(channel)

        try:
            response = stub.GetAllCars(server_services_pb2.GetAllCarsRequest())

            cars = [
                {
                    "vin": car.vin,
                    "condition": car.condition,
                    "odometer": car.odometer,
                    "mmr": car.mmr,
                    "specifications": {
                        "year": car.specifications.year,
                        "make": car.specifications.make,
                        "model": car.specifications.model,
                        "trim": car.specifications.trim,
                        "body": car.specifications.body,
                        "transmission": car.specifications.transmission,
                    },
                    "seller_name": car.seller_name,
                    "seller_state": car.seller_state,
                    "sale_date": car.sale_date,
                    "selling_price": car.selling_price,
                    "seller_coordinates": {
                        "latitude": car.seller_coordinates.latitude,
                        "longitude": car.seller_coordinates.longitude,
                    }
                }
                for car in response.cars
            ]


            return Response(cars, status=status.HTTP_200_OK)

        except grpc.RpcError as e:

            return Response({"error": f"gRPC call failed: {e.details()}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetAllCarsLView_2(APIView):
    def get(self, request):
        channel = grpc.insecure_channel(f'{GRPC_HOST}:{GRPC_PORT}')
        stub = server_services_pb2_grpc.CarServiceDatabaseStub(channel)

        try:
            # Make the gRPC call
            response = stub.GetAllCars(server_services_pb2.GetAllCarsRequest())

            # Build the cities list and ensure unique keys
            cities = []
            for car in response.cars:
                city_data = {
                    "nome": car.seller_state,
                    "latitude": car.seller_coordinates.latitude,
                    "longitude": car.seller_coordinates.longitude,
                    "id": car.vin,
                }

                # Avoid adding duplicates
                if not any(existing["id"] == city_data["id"] for existing in cities):
                    cities.append(city_data)

            # Return sanitized response
            return Response({"cities": cities}, status=status.HTTP_200_OK)

        except grpc.RpcError as e:
            return Response(
                {"error": f"gRPC call failed: {e.details()}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class GetCarByVinLView(APIView):
    def put(self, request):
        vin = request.data.get("id")
        seller_state = request.data.get("name")  # Correctly assign seller_state
        latitude = request.data.get("latitude")
        longitude = request.data.get("longitude")

        # Validate VIN
        if not vin or len(vin) != 17:
            return Response({"error": "VIN must be a 17-character string."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate required fields
        if not seller_state or latitude is None or longitude is None:
            return Response({"error": "All fields (name, latitude, longitude) are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            # Construct the gRPC update request
            update_data = server_services_pb2.UpdateCarRequest(
                vin=vin,
                seller_state=seller_state,
                latitude=latitude,
                longitude=longitude
            )


            logging.debug(f"Sending update data to gRPC: {update_data}")

            channel = grpc.insecure_channel(f'{GRPC_HOST}:{GRPC_PORT}')
            stub = server_services_pb2_grpc.CarServiceDatabaseStub(channel)

            response = stub.UpdateCar(update_data)

            logging.debug(f"gRPC Response: {response}")

            if response.success:
                return Response({"message": "Seller details updated successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": response.message}, status=status.HTTP_400_BAD_REQUEST)

        except grpc.RpcError as e:

            logging.error(f"gRPC call failed: {e.details()}")
            return Response({"error": f"gRPC call failed: {e.details()}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)