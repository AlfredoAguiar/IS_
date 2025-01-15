import xml.etree.ElementTree as ET


class Car:
    def __init__(self, specs, vin, condition, odometer, seller, mmr):
        self.specs = specs
        self.vin = vin
        self.condition = condition
        self.odometer = odometer
        self.seller = seller
        self.mmr = mmr

    def to_xml(self):
        car_el = ET.Element("Car")
        ET.SubElement(car_el, "VIN").text = self.vin
        ET.SubElement(car_el, "Condition").text = str(self.condition)
        ET.SubElement(car_el, "Odometer").text = str(self.odometer)
        ET.SubElement(car_el, "MMR").text = str(self.mmr)

        specs_el = ET.SubElement(car_el, "Specifications")
        ET.SubElement(specs_el, "Year").text = str(self.specs.year)
        ET.SubElement(specs_el, "Make").text = self.specs.make
        ET.SubElement(specs_el, "Model").text = self.specs.model
        ET.SubElement(specs_el, "Trim").text = self.specs.trim
        ET.SubElement(specs_el, "Body").text = self.specs.body
        ET.SubElement(specs_el, "Transmission").text = self.specs.transmission
        ET.SubElement(specs_el, "Color").text = self.specs.color
        ET.SubElement(specs_el, "Interior").text = self.specs.interior

        seller_el = ET.SubElement(car_el, "Seller")
        ET.SubElement(seller_el, "Name").text = self.seller.name
        ET.SubElement(seller_el, "State").text = self.seller.state
        ET.SubElement(seller_el, "SaleDate").text = self.seller.sale_date
        ET.SubElement(seller_el, "SellingPrice").text = self.seller.selling_price


        return car_el
