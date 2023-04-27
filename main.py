import io
import xml.etree.ElementTree as ET
from collections import namedtuple

PADS4 = " "*4


def _get_base_template():
    """
    Internal implementation
    Assume we can retrieve the template from API call or given as *.xml in SimLab
    """
    return """<RenameBody CheckBox="ON" UUID="78633e0d-3d2f-4e9a-b075-7bff122772d8">
    <SupportEntities>
    <Entities>
      <Model>$Geometry</Model>
      <Body>"Body 2",</Body>
    </Entities>
    </SupportEntities>
    <NewName Value="CH"/>
    <Output/>
    </RenameBody>"""


def get_base_template():
    """
    Public user interface for retrieving the template
    """
    return _get_base_template()


def process_data(base_template):
    root = ET.fromstring(base_template)
    Row = namedtuple('Row', 'tag attrib text')
    return (Row(child.tag, child.attrib, child.text)
            for child in root.iter())


def get_template(rootx):
    tree = ET.ElementTree(rootx)
    dummy_file = io.BytesIO()
    tree.write(dummy_file)
    return dummy_file.getvalue().decode("utf-8")


def create_root_elem(child):
    return PADS4 + f"rootx = ET.Element('{child.tag}', {child.attrib})\n"


def create_top_elem(child):
    return PADS4 + f"{child.tag} = ET.Element('{child.tag}', {child.attrib})\n"


def create_sub_elem(child, future_child):
    return PADS4 + f"{future_child.tag} = ET.SubElement({child.tag}, '{future_child.tag}', {future_child.attrib})\n"


def append_to_root(child):
    return PADS4 + f"rootx.append({child.tag})\n"


def append_return():
    return PADS4 + "return rootx\n"


def inject_pseudo_value(child):
    pseudo = f'{child.tag}Value'
    str_a = PADS4 + \
        f"pseudo = kwargs.get(\'{pseudo}\', \'{child.attrib['Value']}\')\n"
    str_b = PADS4 + f"{child.tag}.attrib['Value'] = pseudo\n"
    return str_a + str_b


def inject_pseudo_text(child):
    pseudo = f'{child.tag}Text'
    str_a = PADS4 + f"pseudo = kwargs.get(\'{pseudo}\', \'{child.text}\')\n"
    str_b = PADS4 + f"{child.tag}.text = pseudo\n"
    return str_a + str_b


def parse_root_elem(code_str, child):
    return code_str + create_root_elem(child)


def parse_top_elem(code_str, child):
    sec_str1 = create_top_elem(child)
    if child.attrib:
        sec_str1 += inject_pseudo_value(child)

    sec_str2 = ""
    if child.text is None:
        sec_str2 += PADS4 + f"{child.tag}.text = None\n"

    sec_str3 = append_to_root(child)
    return code_str + sec_str1 + sec_str2 + sec_str3


def parse_supportentities(data, code_str, child):
    """
    <SupportEntities>
      <Entities>
        <Model>$Geometry</Model>
        <Body>"Body 2",</Body>
      </Entities>
    """
    # SupportEntities
    sec_str1 = create_top_elem(child) + append_to_root(child)

    # Entities
    second_child = next(data)
    sec_str2 = create_sub_elem(child, second_child)

    # Model
    third_child = next(data)
    sec_str3 = create_sub_elem(second_child, third_child)
    if third_child.text:
        sec_str3 += inject_pseudo_text(third_child)

    # Body
    fourth_child = next(data)
    # Noted that first one is second_child instead of third_chid
    sec_str4 = create_sub_elem(second_child, fourth_child)
    if fourth_child.text:
        sec_str4 += inject_pseudo_text(fourth_child)

    return code_str + sec_str1 + sec_str2 + sec_str3 + sec_str4


# data : Generator[Row(tag, attrib, text)]
base_template = get_base_template()
data = process_data(base_template)

# meta-programming
# TODO!: Move to a function or try metaclass(__new__, __call__, __init__)
# Noted that padding might become an issue by using the function or class approach
code_str = "def get_tree(**kwargs):\n"
code_str = parse_root_elem(code_str, next(data))

while True:
    try:
        child = next(data)
    except StopIteration:
        break
    else:
        if child.text is None:  # top element
            code_str = parse_top_elem(code_str, child)
        # Grouped element(need other elif to expand other groups)
        elif child.tag == "SupportEntities":
            code_str = parse_supportentities(data, code_str, child)
        else:  # Not grouped element and with child.text
            pass

code_str += append_return()
print(f'{code_str=}')
exec(code_str)


# base_template
print(f'{base_template=}')

# get default value
rootx1 = get_tree()
xm11 = get_template(rootx1)
print(f'{xm11=}')

# now we can inject the value and text
# TODO!: Handle duplicate grouped elements
rootx2 = get_tree(NewNameValue="NewName",
                  BodyText='"Body 9",',
                  ModelText="$AnotherGeoIsOk")
xm12 = get_template(rootx2)
print(f'{xm12=}')
