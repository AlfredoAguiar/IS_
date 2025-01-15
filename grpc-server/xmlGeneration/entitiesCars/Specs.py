import xml.etree.ElementTree as ET


class Specs:
    def __init__(self, year, make, model, trim, body, transmission, color, interior):
        self.year = year
        self.make = make
        self.model = model
        self.trim = trim
        self.body = body
        self.transmission = transmission
        self.color = color
        self.interior = interior

    def to_xml(self):
        specs_el = ET.Element("Specifications")
        ET.SubElement(specs_el, "Year").text = self.year
        ET.SubElement(specs_el, "Make").text = self.make
        ET.SubElement(specs_el, "Model").text = self.model
        ET.SubElement(specs_el, "Trim").text = self.trim
        ET.SubElement(specs_el, "Body").text = self.body
        ET.SubElement(specs_el, "Transmission").text = self.transmission
        ET.SubElement(specs_el, "Color").text = self.color
        ET.SubElement(specs_el, "Interior").text = self.interior
        return specs_el
