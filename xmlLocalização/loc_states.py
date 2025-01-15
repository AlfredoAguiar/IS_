import xml.etree.ElementTree as ET
import xml.dom.minidom

# Paths to input and output files
cars_file = "../dt/car_prices.xml"  # Ficheiro de entrada com carros
coordinates_file = "dt/unique_States_coordinates.xml"  # Ficheiro com coordenadas
output_file = "../dt/car_prices_cord.xml"  # Ficheiro de saída com carros e coordenadas

def add_location_to_car(car, city, latitude, longitude):
    """
    Adds location information (city, latitude, longitude) to a car.
    """
    loc = ET.SubElement(car, "Location")
    city_element = ET.SubElement(loc, "City")
    city_element.text = city

    coordinates = ET.SubElement(loc, "Coordinates")
    latitude_element = ET.SubElement(coordinates, "Latitude")
    latitude_element.text = f"{latitude:.7f}"
    longitude_element = ET.SubElement(coordinates, "Longitude")
    longitude_element.text = f"{longitude:.7f}"


def format_and_save_xml(tree, output_file):
    rough_string = ET.tostring(tree.getroot(), encoding="utf-8")
    reparsed = xml.dom.minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ")
    cleaned_xml = "\n".join(line for line in pretty_xml.splitlines() if line.strip())

    with open(output_file, "w", encoding="utf-8") as file:
        file.write(cleaned_xml)


try:
    cars_tree = ET.parse(cars_file)
    cars_root = cars_tree.getroot()

    coordinates_tree = ET.parse(coordinates_file)
    coordinates_root = coordinates_tree.getroot()
except ET.ParseError as e:
    print(f"Error parsing XML files: {e}")
    exit()

city_coordinates = {}
for state_element in coordinates_root.findall(".//State"):
    state_name = state_element.text.strip().upper()  # Normalize to uppercase
    coordinates_element = state_element.find("Coordinates")
    if coordinates_element is not None:
        try:
            latitude = float(coordinates_element.find("Latitude").text)
            longitude = float(coordinates_element.find("Longitude").text)
            city_coordinates[state_name] = (latitude, longitude)
        except (AttributeError, ValueError):
            print(f"Invalid coordinates for state: {state_name}")

for car in cars_root.findall(".//Car"):
    seller_state_element = car.find(".//Seller/State")
    if seller_state_element is not None:
        state_name = seller_state_element.text.strip().upper()  # Normalize to uppercase
        if state_name in city_coordinates:
            latitude, longitude = city_coordinates[state_name]
            add_location_to_car(car, state_name, latitude, longitude)
        else:
            print(f"Coordinates not found for state: {state_name}")

try:
    format_and_save_xml(cars_tree, output_file)
    print(f"Updated XML saved to {output_file}")
except Exception as e:
    print(f"Error saving the XML file: {e}")



