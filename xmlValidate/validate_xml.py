from lxml import etree


def validate_xml():
    try:

        with open("../dt/car_prices_cord.xml", "r") as file:
            xml_doc = etree.parse(file)

        schema_path = "schema.xsd"

        with open(schema_path, "r") as schema_file:
            xml_schema_doc = etree.parse(schema_file)
            xml_schema = etree.XMLSchema(xml_schema_doc)

        if xml_schema.validate(xml_doc):
            return "XML is valid."
        else:
            return f"XML is not valid. Errors: {xml_schema.error_log}"

    except etree.XMLSyntaxError as e:
        return f"Error parsing XML: {e}"
    except etree.XMLSchemaParseError as e:
        return f"Error parsing XSD schema: {e}"
    except Exception as e:
        return f"An error occurred: {e}"


result = validate_xml()
print(result)
