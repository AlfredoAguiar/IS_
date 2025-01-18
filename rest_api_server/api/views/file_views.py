from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..serializers.file_serializer import FileUploadSerializer
import grpc
from api.grpc_ import server_services_pb2 as server_services_pb2
from api.grpc_ import server_services_pb2_grpc as server_services_pb2_grpc
import os
from rest_api_server.settings import GRPC_PORT, GRPC_HOST


class FileUploadView(APIView):
    def post(self, request):
        # Valida os dados do request usando o serializer
        serializer = FileUploadSerializer(data=request.data)
        
        # Se os dados forem válidos, pega o arquivo
        if serializer.is_valid():
            file = serializer.validated_data['file']
        
            # Verifica se o arquivo foi enviado
            if not file:
                return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Obtém o nome e a extensão do arquivo
            file_name, file_extension = os.path.splitext(file.name)
            
            # Lê o conteúdo do arquivo
            file_content = file.read()
            
            # Conecta ao serviço gRPC
            channel = grpc.insecure_channel(f'{GRPC_HOST}:{GRPC_PORT}')
            stub = server_services_pb2_grpc.SendFileServiceStub(channel)
            
            # Prepara a requisição gRPC
            grpc_request = server_services_pb2.SendFileRequestBody(
                file_name=file_name,
                file_mime=file_extension,
                file=file_content
            )
            
            # Envia os dados do arquivo ao serviço gRPC
            try:
                stub.SendFile(grpc_request)  # Envia a requisição sem atribuí-la a `response`
                
                # Retorna a resposta de sucesso
                return Response({
                    "file_name": file_name,
                    "file_extension": file_extension
                }, status=status.HTTP_201_CREATED)
            
            except grpc.RpcError as e:
                # Se a chamada gRPC falhar, retorna o erro
                return Response({
                    "error": f"gRPC call failed: {e.details()}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Se o serializer não for válido, retorna os erros do serializer
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

            # Conectar ao serviço gRPC
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
        if not vin or len(vin) != 17:
            return Response({"error": "VIN must be a 17-character string."}, status=status.HTTP_400_BAD_REQUEST)

        # Prepare the data to send to the gRPC service
        update_data = server_services_pb2.UpdateCarRequest(
            vin=vin,
            condition=request.data.get("condition"),
            odometer=request.data.get("odometer"),
            color=request.data.get("color", ""),
            interior=request.data.get("interior", ""),
            mmr=request.data.get("mmr"),
            specifications=server_services_pb2.Specifications(
                year=request.data.get("year"),
                make=request.data.get("make"),
                model=request.data.get("model"),
                trim=request.data.get("trim"),
                body=request.data.get("body"),
                transmission=request.data.get("transmission")
            ),
            seller_name=request.data.get("seller_name"),
            seller_state=request.data.get("seller_state"),
            sale_date=request.data.get("sale_date"),
            selling_price=request.data.get("selling_price"),
            city=request.data.get("city"),
            latitude=request.data.get("latitude"),
            longitude=request.data.get("longitude")
        )

        # Connect to the gRPC service
        channel = grpc.insecure_channel(f'{GRPC_HOST}:{GRPC_PORT}')
        stub = server_services_pb2_grpc.CarServiceDatabaseStub(channel)

        try:
            # Send the update request to the gRPC service
            response = stub.UpdateCar(update_data)

            if response.success:
                return Response({"message": "Car updated successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": response.message}, status=status.HTTP_400_BAD_REQUEST)

        except grpc.RpcError as e:
            return Response({"error": f"gRPC call failed: {e.details()}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteCarView(APIView):
    def delete(self, request):
        vin = request.data.get("vin")
        if not vin or len(vin) != 17:
            return Response({"error": "VIN must be a 17-character string."}, status=status.HTTP_400_BAD_REQUEST)

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