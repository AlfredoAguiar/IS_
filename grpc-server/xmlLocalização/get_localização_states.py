import xml.dom.minidom
import requests
import time
import os

# Mapeamento das abreviações para os nomes completos dos estados
state_abbreviations = {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California',
    'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia',
    'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa',
    'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
    'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri',
    'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey',
    'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio',
    'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
    'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont',
    'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming'
}

class StateCoordinatesUpdater:
    def __init__(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path

    def get_coordinates(self, state_abbr):
        """
        Obtém as coordenadas de latitude e longitude para um estado utilizando a API Nominatim do OpenStreetMap.
        """
        state_name = state_abbreviations.get(state_abbr.upper(), state_abbr)

        base_url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': state_name,  # Parâmetro de consulta para o estado
            'format': 'json',  # Formato JSON para a resposta
            'addressdetails': 1,  # Detalhes do endereço
            'limit': 1,  # Limita o número de resultados
            'countrycodes': 'US'  # Limita os resultados aos Estados Unidos
        }
        headers = {
            'User-Agent': 'YourProjectName/1.0 (your_email@example.com)'  # Modifique conforme necessário
        }

        try:
            response = requests.get(base_url, params=params, headers=headers,
                                    timeout=20)  # Aumentando o timeout para 20 segundos
            response.raise_for_status()  # Verifica se a requisição foi bem-sucedida

            data = response.json()

            if data:
                latitude = data[0]['lat']
                longitude = data[0]['lon']
                print(f"Successfully fetched coordinates for {state_name}: Latitude {latitude}, Longitude {longitude}")
                return latitude, longitude
            else:
                print(f"No coordinates found for state: {state_name}")
        except requests.Timeout:
            print(f"Request timed out while fetching coordinates for {state_name}. Retrying...")
            time.sleep(5)
            return self.get_coordinates(state_abbr)
        except requests.RequestException as e:
            print(f"Error fetching coordinates for {state_name}: {e}")
            return None, None

    def update_xml_with_coordinates(self):
        """
        Atualiza o arquivo XML com as coordenadas de latitude e longitude de cada estado.
        """
        if not os.path.exists(self.input_path):
            print(f"Input file {self.input_path} not found.")
            return

        try:
            doc = xml.dom.minidom.parse(self.input_path)
            states_elements = doc.getElementsByTagName("State")

            for state_element in states_elements:
                state_abbr = state_element.firstChild.nodeValue.strip()
                print(f"Processing state: {state_abbr}")

                if not state_abbr:
                    print(f"Skipping empty state abbreviation")
                    continue

                latitude, longitude = self.get_coordinates(state_abbr)
                time.sleep(1)

                if latitude and longitude:
                    coordinates_element = doc.createElement("Coordinates")
                    state_element.appendChild(coordinates_element)

                    latitude_element = doc.createElement("Latitude")
                    latitude_element.appendChild(doc.createTextNode(str(latitude)))
                    coordinates_element.appendChild(latitude_element)

                    longitude_element = doc.createElement("Longitude")
                    longitude_element.appendChild(doc.createTextNode(str(longitude)))
                    coordinates_element.appendChild(longitude_element)
                else:
                    print(f"Skipping coordinates for {state_abbr} due to missing data")

            # Salva o XML atualizado
            with open(self.output_path, "w", encoding="utf-8") as file:
                doc.writexml(file, indent="\n", addindent="  ", newl="\n")
            print(f"Updated XML saved to {self.output_path}")

        except Exception as e:
            print(f"Error processing XML: {e}")