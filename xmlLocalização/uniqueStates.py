import xml.etree.ElementTree as ET

xml_path = "../dt/car_prices.xml"

valid_states = {
    "pr", "tn", "mn", "ut", "on", "mi", "nv", "fl", "or", "ms", "ok", "md", "nm", "hi", "oh",
    "ns", "pa", "ny", "ne", "co", "il", "mo", "in", "tx", "sc", "nc", "ma", "va", "ga", "ca",
    "nj", "wa", "az", "wi", "qc", "al", "la"
}

tree = ET.parse(xml_path)
root = tree.getroot()

unique_states = set()

for car in root.findall('.//Car'):

    seller_element = car.find('Seller')
    if seller_element is not None:

        state_element = seller_element.find('State')
        if state_element is not None:
            state = state_element.text.strip().lower()

            if state in valid_states:
                unique_states.add(state)

output_root = ET.Element("States")

# Para cada estado único encontrado, criar um elemento <State>
for state in unique_states:
    state_element = ET.SubElement(output_root, "State")
    state_element.text = state.upper()

output_tree = ET.ElementTree(output_root)

output_tree.write("dt/unique_States.xml", encoding="utf-8", xml_declaration=True)

print("Ficheiro XML com estados únicos foi salvo em: dt/unique_States.xml")
