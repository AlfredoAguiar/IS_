import xml.etree.ElementTree as ET
import xml.dom.minidom


class XMLLocationUpdater:
    def __init__(self, cars_file, coordinates_file, output_file):
        self.cars_file = cars_file
        self.coordinates_file = coordinates_file
        self.output_file = output_file

    def add_location_to_car(self, car, city, latitude, longitude):

        loc = ET.SubElement(car, "Location")
        city_element = ET.SubElement(loc, "City")
        city_element.text = city

        coordinates = ET.SubElement(loc, "Coordinates")
        latitude_element = ET.SubElement(coordinates, "Latitude")
        latitude_element.text = f"{latitude:.7f}"
        longitude_element = ET.SubElement(coordinates, "Longitude")
        longitude_element.text = f"{longitude:.7f}"

    def format_and_save_xml(self, tree):

        rough_string = ET.tostring(tree.getroot(), encoding="utf-8")
        reparsed = xml.dom.minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ")
        cleaned_xml = "\n".join(line for line in pretty_xml.splitlines() if line.strip())

        with open(self.output_file, "w", encoding="utf-8") as file:
            file.write(cleaned_xml)

    def update_locations(self):

        try:
            cars_tree = ET.parse(self.cars_file)
            cars_root = cars_tree.getroot()

            coordinates_tree = ET.parse(self.coordinates_file)
            coordinates_root = coordinates_tree.getroot()

            city_coordinates = {}
            for location_element in coordinates_root.findall(".//Location"):
                city_name = location_element.find("City").text.strip().upper()
                coordinates_element = location_element.find("Coordinates")
                if coordinates_element is not None:
                    try:
                        latitude = float(coordinates_element.find("Latitude").text)
                        longitude = float(coordinates_element.find("Longitude").text)
                        city_coordinates[city_name] = (latitude, longitude)
                    except (AttributeError, ValueError):
                        print(f"Invalid coordinates for city: {city_name}")

            for car in cars_root.findall(".//Car"):
                seller_city_element = car.find(".//Seller/City")
                if seller_city_element is not None:
                    city_name = seller_city_element.text.strip().upper()
                    if city_name in city_coordinates:
                        latitude, longitude = city_coordinates[city_name]
                        self.add_location_to_car(car, city_name, latitude, longitude)
                    else:
                        print(f"Coordinates not found for city: {city_name}")

            # Save the updated XML with location data
            self.format_and_save_xml(cars_tree)
            print(f"Updated XML saved to {self.output_file}")

        except Exception as e:
            print(f"Error updating locations: {str(e)}")
            raise e



