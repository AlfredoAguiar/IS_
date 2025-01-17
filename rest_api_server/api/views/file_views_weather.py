from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..serializers.file_serializer import FileUploadSerializer
import grpc
from api.grpc_2 import server_services_w_pb2 as server_services_pb2
from api.grpc_2 import server_services_w_pb2_grpc as server_services_pb2_grpc
import os
from rest_api_server.settings import GRPC_PORT_2, GRPC_HOST_2
from datetime import datetime

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
            channel = grpc.insecure_channel(f'{GRPC_HOST_2}:{GRPC_PORT_2}')
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
            channel = grpc.insecure_channel(f'{GRPC_HOST_2}:{GRPC_PORT_2}')
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

class GetWeatherByRegionView(APIView):
    def get(self, request):
        """
        Filters weather data by region.
        """
        region = request.query_params.get("region")
        if not region:
            return Response({"error": "Region parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        channel = grpc.insecure_channel(f'{GRPC_HOST_2}:{GRPC_PORT_2}')
        stub = server_services_pb2_grpc.WeatherServiceStub(channel)

        try:
            # Query gRPC service for weather data by region
            grpc_request = server_services_pb2.GetWeatherByRegionRequest(region=region)
            response = stub.GetWeatherByRegion(grpc_request)

            if not response.weather_data:
                return Response({"error": "No weather data found for the specified region."}, status=status.HTTP_404_NOT_FOUND)

            weather_data = [
                {
                    "region": data.region,
                    "country": data.country,
                    "city": data.city,
                    "date": data.date,
                    "avg_temperature": data.avg_temperature,
                    "coordinates": {
                        "latitude": data.coordinates.latitude,
                        "longitude": data.coordinates.longitude
                    }
                }
                for data in response.weather_data
            ]

            return Response(weather_data, status=status.HTTP_200_OK)

        except grpc.RpcError as e:
            return Response({"error": f"gRPC call failed: {e.details()}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class GetWeatherByLocationView(APIView):
    def get(self, request):
        """
        Filters weather data by city and country.
        """
        city = request.query_params.get("city")
        country = request.query_params.get("country")

        # Check if both city and country are provided
        if not city or not country:
            return Response({"error": "City and country parameters are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Connect to the gRPC service
        channel = grpc.insecure_channel(f'{GRPC_HOST_2}:{GRPC_PORT_2}')
        stub = server_services_pb2_grpc.WeatherServiceStub(channel)

        try:
            # Send a gRPC request to get weather data by city and country
            grpc_request = server_services_pb2.GetWeatherByLocationRequest(country=country, city=city)
            response = stub.GetWeatherByLocation(grpc_request)


            if not response.weather_data:
                return Response({"error": "No weather data found for the specified location."}, status=status.HTTP_404_NOT_FOUND)


            weather_data = []
            if isinstance(response.weather_data, list):
                weather_data = response.weather_data
            else:

                weather_data.append(response.weather_data)

            # Format the response data
            formatted_weather_data = [
                {
                    "region": data.region,
                    "country": data.country,
                    "city": data.city,
                    "date": data.date,
                    "avg_temperature": data.avg_temperature,
                    "coordinates": {
                        "latitude": data.coordinates.latitude,
                        "longitude": data.coordinates.longitude
                    }
                }
                for data in weather_data
            ]

            # Return the weather data as a JSON response
            return Response(formatted_weather_data, status=status.HTTP_200_OK)

        except grpc.RpcError as e:
            # If there is an error with the gRPC request
            return Response({"error": f"gRPC call failed: {e.details()}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetWeatherByDateRangeView(APIView):
    def get(self, request):
        """
        Filters weather data by date range and returns it.
        """
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        # Check if both start_date and end_date are provided
        if not start_date or not end_date:
            return Response({"error": "start_date and end_date are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate date format (YYYY-MM-DD)
        try:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        # Connect to the gRPC service
        channel = grpc.insecure_channel(f'{GRPC_HOST_2}:{GRPC_PORT_2}')
        stub = server_services_pb2_grpc.WeatherServiceStub(channel)

        try:
            # Send a gRPC request to get weather data within the date range
            grpc_request = server_services_pb2.GetWeatherByDateRangeRequest(
                start_date=start_date,  # Pass the date range
                end_date=end_date
            )
            response = stub.GetWeatherByDateRange(grpc_request)

            # Check if we have weather data in the response
            if not response.weather_data:
                return Response({"error": "No weather data found for the specified date range."}, status=status.HTTP_404_NOT_FOUND)

            # Handle response to ensure it is iterable (and iterate over repeated fields)
            formatted_weather_data = []
            for data in response.weather_data:
                # Access the individual fields in each 'data' object (not a container)
                try:
                    # Parsing the date from the weather data
                    date_obj = datetime.strptime(data.date, "%m/%d/%Y")
                    formatted_date = date_obj.strftime("%Y-%m-%d")
                except ValueError:
                    formatted_date = data.date  # Fallback if the date format differs

                # Append the formatted data to the response list
                formatted_weather_data.append({
                    "region": data.region,
                    "country": data.country,
                    "city": data.city,
                    "date": formatted_date,  # Use the formatted date
                    "avg_temperature": data.avg_temperature,
                    "coordinates": {
                        "latitude": data.coordinates.latitude,
                        "longitude": data.coordinates.longitude
                    }
                })

            # Return the filtered and formatted weather data
            return Response(formatted_weather_data, status=status.HTTP_200_OK)

        except grpc.RpcError as e:
            # If there is an error with the gRPC request
            return Response({"error": f"gRPC call failed: {e.details()}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)