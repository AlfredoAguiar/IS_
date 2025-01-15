import xml.etree.ElementTree as ET
import xml.dom.minidom as md
from xmlGeneration.entitiesCars.Car_ import Car
from xmlGeneration.entitiesCars.Specs import Specs
from xmlGeneration.entitiesCars.Seller import Seller
from xmlGeneration.csv_reader import CSVReader

valid_states = {
    "pr", "tn", "mn", "ut", "on", "mi", "nv", "fl", "or", "ms", "ok", "md", "nm", "hi", "oh",
    "ns", "pa", "ny", "ne", "co", "il", "mo", "in", "tx", "sc", "nc", "ma", "va", "ga", "ca",
    "nj", "wa", "az", "wi", "qc", "al", "la"
}


class CSVtoXMLConverter:
    def __init__(self, csv_path, output_path):
        self._reader = CSVReader(csv_path)
        self.output_path = output_path

    def to_xml(self):
        cars = self._reader.read_entities(
            attr="vin",
            builder=lambda row: Car(
                vin=row["vin"],
                condition=row["condition"],
                odometer=row["odometer"],
                mmr=row["mmr"],
                specs=Specs(
                    year=row["year"],
                    make=row["make"],
                    model=row["model"],
                    trim=row["trim"],
                    body=row["body"],
                    transmission=row["transmission"],
                    color=row["color"],
                    interior=row["interior"]
                ),
                seller=Seller(
                    name=row["seller"],
                    state=row["state"],
                    selling_price=row["sellingprice"],
                    sale_date=row["saledate"],
                ),
            )
        )

        root_el = ET.Element("Cars")

        for car in cars.values():
            seller_state = car.seller.state.strip().lower()
            if seller_state in valid_states:
                root_el.append(car.to_xml())
            else:
                print(f"Car with VIN {car.vin} has an invalid state: {seller_state}. Skipping.")

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