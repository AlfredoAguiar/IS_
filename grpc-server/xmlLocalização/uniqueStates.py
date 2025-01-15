import xml.etree.ElementTree as ET


def uniqueStates(xml_path, output_path):
    # Definir os estados válidos
    valid_states = {
        "pr", "tn", "mn", "ut", "on", "mi", "nv", "fl", "or", "ms", "ok", "md", "nm", "hi", "oh",
        "ns", "pa", "ny", "ne", "co", "il", "mo", "in", "tx", "sc", "nc", "ma", "va", "ga", "ca",
        "nj", "wa", "az", "wi", "qc", "al", "la"
    }

    try:
        # Parse o XML
        tree = ET.parse(xml_path)
        root = tree.getroot()

        # Criar um conjunto para armazenar estados únicos
        unique_states = set()

        # Procurar os estados no XML
        for car in root.findall('.//Car'):
            seller_element = car.find('Seller')
            if seller_element is not None:
                state_element = seller_element.find('State')
                if state_element is not None:
                    state = state_element.text.strip().lower()

                    # Verificar se o estado está na lista de estados válidos
                    if state in valid_states:
                        unique_states.add(state)

        # Criar o XML de saída com os estados únicos
        output_root = ET.Element("States")

        # Para cada estado único, criar um elemento <State>
        for state in unique_states:
            state_element = ET.SubElement(output_root, "State")
            state_element.text = state.upper()

        # Gerar o arquivo XML com estados únicos
        output_tree = ET.ElementTree(output_root)
        output_tree.write(output_path, encoding="utf-8", xml_declaration=True)

        print(f"Ficheiro XML com estados únicos foi salvo em: {output_path}")

    except Exception as e:
        print(f"Erro ao processar o XML: {e}")