import xml.etree.ElementTree as ET


class Seller:
    def __init__(self, name, state, sale_date, selling_price):
        self.name = name
        self.state = state
        self.selling_price = selling_price
        self.sale_date = sale_date

    def to_xml(self):
        seller_el = ET.Element("Seller")
        ET.SubElement(seller_el, "Name").text = self.name
        ET.SubElement(seller_el, "State").text = self.state
        ET.SubElement(seller_el, "SaleDate").text = self.sale_date
        ET.SubElement(seller_el, "SellingPrice").text = self.selling_price
        return seller_el
