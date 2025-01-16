import xml.etree.ElementTree as ET
import xml.dom.minidom as md
from xmlGeneration.csv_reader import CSVReader

class WeatherData:
    def __init__(self, region, country, state, city, month, day, year, avg_temperature):
        self.region = region
        self.country = country
        self.state = state
        self.city = city
        self.month = month
        self.day = day
        self.year = year
        self.avg_temperature = avg_temperature

    def to_xml(self):
        weather_el = ET.Element("WeatherData")

        region_el = ET.SubElement(weather_el, "Region")
        region_el.text = self.region

        country_el = ET.SubElement(weather_el, "Country")
        country_el.text = self.country

        state_el = ET.SubElement(weather_el, "State")
        state_el.text = self.state

        city_el = ET.SubElement(weather_el, "City")
        city_el.text = self.city

        date_el = ET.SubElement(weather_el, "Date")
        date_el.text = f"{self.month}/{self.day}/{self.year}"

        temperature_el = ET.SubElement(weather_el, "AvgTemperature")
        temperature_el.text = str(self.avg_temperature)

        return weather_el


class CSVtoXMLConverter:
    def __init__(self, csv_path, output_path):
        self._reader = CSVReader(csv_path)  # Assuming CSVReader is reading the file correctly
        self.output_path = output_path

    def to_xml(self):
        weather_data = self._reader.read_entities(
            attr="Region",
            builder=lambda row: WeatherData(
                region=row["Region"],
                country=row["Country"],
                state=row["State"],
                city=row["City"],
                month=row["Month"],
                day=row["Day"],
                year=row["Year"],
                avg_temperature=row["AvgTemperature"]
            )
        )

        root_el = ET.Element("WeatherReports")

        for data in weather_data.values():
            root_el.append(data.to_xml())

        return root_el

    def to_xml_str(self):
        xml_str = ET.tostring(self.to_xml(), encoding="utf8", method="xml").decode()

        # Format with indentation (prettify XML)
        dom = md.parseString(xml_str)
        pretty_xml = dom.toprettyxml()

        return pretty_xml

    def save_to_file(self):
        xml_string = self.to_xml_str()

        with open(self.output_path, "w", encoding="utf-8") as file:
            file.write(xml_string)