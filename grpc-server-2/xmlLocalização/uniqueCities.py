import xml.etree.ElementTree as ET

def uniqueCities(xml_path, output_path):
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()

        unique_cities = set()

        for weather_data in root.findall('.//WeatherData'):
            city_element = weather_data.find('City')
            if city_element is not None:
                city = city_element.text.strip()

                if city:
                    unique_cities.add(city)

        output_root = ET.Element("Cities")

        for city in unique_cities:
            city_element = ET.SubElement(output_root, "City")
            city_element.text = city

        output_tree = ET.ElementTree(output_root)
        output_tree.write(output_path, encoding="utf-8", xml_declaration=True)

        print(f"Ficheiro XML com cidades únicas foi salvo em: {output_path}")

    except Exception as e:
        print(f"Erro ao processar o XML: {e}")