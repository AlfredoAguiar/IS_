
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
        """
        Formats the XML data to be human-readable and saves it to the output file.
        """
        rough_string = ET.tostring(tree.getroot(), encoding="utf-8")
        reparsed = xml.dom.minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ")
        cleaned_xml = "\n".join(line for line in pretty_xml.splitlines() if line.strip())

        with open(self.output_file, "w", encoding="utf-8") as file:
            file.write(cleaned_xml)

    def update_locations(self):
        """
        Update the car XML with location data based on state information from the coordinates file.
        """
        try:
            # Parse the XML files
            cars_tree = ET.parse(self.cars_file)
            cars_root = cars_tree.getroot()

            coordinates_tree = ET.parse(self.coordinates_file)
            coordinates_root = coordinates_tree.getroot()

            # Create a mapping of state names to coordinates
            city_coordinates = {}
            for state_element in coordinates_root.findall(".//State"):
                state_name = state_element.text.strip().upper()
                coordinates_element = state_element.find("Coordinates")
                if coordinates_element is not None:
                    try:
                        latitude = float(coordinates_element.find("Latitude").text)
                        longitude = float(coordinates_element.find("Longitude").text)
                        city_coordinates[state_name] = (latitude, longitude)
                    except (AttributeError, ValueError):
                        print(f"Invalid coordinates for state: {state_name}")

            # Add location data to each car based on state
            for car in cars_root.findall(".//Car"):
                seller_state_element = car.find(".//Seller/State")
                if seller_state_element is not None:
                    state_name = seller_state_element.text.strip().upper()
                    if state_name in city_coordinates:
                        latitude, longitude = city_coordinates[state_name]
                        self.add_location_to_car(car, state_name, latitude, longitude)
                    else:
                        print(f"Coordinates not found for state: {state_name}")

            # Save the updated XML with location data
            self.format_and_save_xml(cars_tree)
            print(f"Updated XML saved to {self.output_file}")

        except Exception as e:
            print(f"Error updating locations: {str(e)}")
            raise e




