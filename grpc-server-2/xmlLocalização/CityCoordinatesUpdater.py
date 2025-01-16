import xml.dom.minidom
import requests
import time
import os


class CityCoordinatesUpdater:
    def __init__(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path

    def get_coordinates(self, city_name, country_name):
        """
        Obtém as coordenadas de latitude e longitude para uma cidade utilizando a API Nominatim do OpenStreetMap.
        """
        base_url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': f"{city_name}, {country_name}",  # Parâmetro de consulta para cidade e país
            'format': 'json',  # Formato JSON para a resposta
            'addressdetails': 1,  # Detalhes do endereço
            'limit': 1,  # Limita o número de resultados
        }
        headers = {
            'User-Agent': 'YourProjectName/1.0 (your_email@example.com)'  # Modifique conforme necessário
        }

        try:
            response = requests.get(base_url, params=params, headers=headers, timeout=20)
            response.raise_for_status()  # Verifica se a requisição foi bem-sucedida

            data = response.json()

            if data:
                latitude = data[0]['lat']
                longitude = data[0]['lon']
                print(
                    f"Successfully fetched coordinates for {city_name}, {country_name}: Latitude {latitude}, Longitude {longitude}")
                return latitude, longitude
            else:
                print(f"No coordinates found for city: {city_name}, {country_name}")
        except requests.Timeout:
            print(f"Request timed out while fetching coordinates for {city_name}, {country_name}. Retrying...")
            time.sleep(5)
            return self.get_coordinates(city_name, country_name)
        except requests.RequestException as e:
            print(f"Error fetching coordinates for {city_name}, {country_name}: {e}")
            return None, None

    def update_xml_with_coordinates(self):
        """
        Atualiza o arquivo XML com as coordenadas de latitude e longitude de cada cidade.
        """
        if not os.path.exists(self.input_path):
            print(f"Input file {self.input_path} not found.")
            return

        try:
            doc = xml.dom.minidom.parse(self.input_path)
            weather_data_elements = doc.getElementsByTagName("WeatherData")

            for weather_data_element in weather_data_elements:
                # Extraímos cidade e país do XML
                city_element = weather_data_element.getElementsByTagName("City")[0]
                country_element = weather_data_element.getElementsByTagName("Country")[0]

                city_name = city_element.firstChild.nodeValue.strip()
                country_name = country_element.firstChild.nodeValue.strip()

                print(f"Processing city: {city_name}, Country: {country_name}")

                if not city_name or not country_name:
                    print(f"Skipping city due to missing name or country")
                    continue

                latitude, longitude = self.get_coordinates(city_name, country_name)
                time.sleep(1)

                if latitude and longitude:
                    # Criar o elemento de coordenadas e adicionar ao XML
                    coordinates_element = doc.createElement("Coordinates")
                    weather_data_element.appendChild(coordinates_element)

                    latitude_element = doc.createElement("Latitude")
                    latitude_element.appendChild(doc.createTextNode(str(latitude)))
                    coordinates_element.appendChild(latitude_element)

                    longitude_element = doc.createElement("Longitude")
                    longitude_element.appendChild(doc.createTextNode(str(longitude)))
                    coordinates_element.appendChild(longitude_element)
                else:
                    print(f"Skipping coordinates for {city_name} due to missing data")

            # Salva o XML atualizado
            with open(self.output_path, "w", encoding="utf-8") as file:
                doc.writexml(file, indent="\n", addindent="  ", newl="\n")
            print(f"Updated XML saved to {self.output_path}")

        except Exception as e:
            print(f"Error processing XML: {e}")