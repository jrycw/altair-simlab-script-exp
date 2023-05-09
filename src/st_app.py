import io
import xml
import xml.etree.ElementTree as ET

import streamlit as st

PADS4 = " "*4


def _get_base_template1():
    return """<ImportParasolid gda="" CheckBox="ON" Type="Parasolid" UUID="400d622c-e74a-4f87-bc0b-af51659b9b6d">
  <tag Value="1"/>
  <FileName widget="LineEdit" Value="./../Input/s4_engine_dummy1.xmt_txt" HelpStr="File name to be imported."/>
  <Units Value="MilliMeter" HelpStr="Units to which this file is to be imported into"/>
  <SolidBodyType Value="1"/>
  <SheetBodyType Value="0"/>
  <WireBodyType Value="0"/>
  <ConnectedBodyType Value="1"/>
  <ImportasFacets Value="0"/>
  <Imprint Value="0"/>
  <Groups Value="1"/>
  <Merge Value="0"/>
  <ImportAssemblyStructure Value="1"/>
  <SaveGeometryInDatabase Value="1"/>
  <AddToExistingModel Value="0"/>
  <MassProperties Value="0"/>
  <FileCount value="0" Value="0"/>
  <Output widget="NULL"/>
  <ImportOption Value="1"/>
  <TransXmlFileName Value=""/>
  <TransOutFileName Value=""/>
 </ImportParasolid>"""


def _get_base_template2():
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


def _get_base_template3():
    return """<SelectFeatures CheckBox="ON" UUID="CF82E8FB-9B3E-4c02-BA93-9466C1342C6E">
  <SupportEntities>
   <Entities>
    <Model>$Geometry</Model>
    <Body>"CC",</Body>
   </Entities>
  </SupportEntities>
  <Arcs MaxValue="0 mm" Value="0" MinValue="0 mm"/>
  <ArcsAll Value="0"/>
  <Circles MaxValue="0 mm" Value="0" MinValue="0 mm"/>
  <CirclesAll Value="0"/>
  <Cones MaxValue="0 mm" Value="0" MinValue="0 mm"/>
  <ConeAll Value="0"/>
  <FullCone Value="0"/>
  <ClosedPartialCone Value="0"/>
  <OpenPartialCone Value="0"/>
  <Dics MaxValue="0 mm" Value="0" MinValue="0 mm"/>
  <DicsAll Value="0"/>
  <HollowDics MaxValue="0 mm" Value="0" MinValue="0 mm"/>
  <HollowDicsAll Value="0"/>
  <Cylinders MaxValue="500 mm" Value="1" MinValue="0 mm"/>
  <CylindersAll Value="0"/>
  <FullCylinder Value="1"/>
  <ClosedPartialCylinder Value="0"/>
  <OpenPartialCylinder Value="0"/>
  <Fillets MaxValue="0 mm" Value="0" MinValue="0 mm"/>
  <FilletsOption Value="1"/>
  <PlanarFaces Value="0"/>
  <FourEdgedFaces Value="0"/>
  <ConnectedCoaxialFaces Value="0"/>
  <ThroughBoltHole MaxValue="0 mm" Value="0" MinValue="0 mm"/>
  <BlindBoltHole MaxValue="0 mm" Value="0" MinValue="0 mm"/>
  <BlindBoltHoleDepth MaxValue="0 mm" Value="0" MinValue="0 mm"/>
  <SlotEdges MaxValue="0 mm" Value="0" MinValue="0 mm"/>
  <SlotEdgesAll Value="0"/>
  <CreateGrp Value="1" Name="Bolt_Thread"/>
  <ArcLengthBased Value=""/>
  <AngleBased Value=""/>
  <SharpEdges Value="" Angle="" Option=""/>
 </SelectFeatures>"""


def _get_base_template4():
    return """<HexBolt pixmap="hexbolt" UUID="17e5a77d-8b12-4228-bae9-59fc362fefaf">
  <tag Value="-1"/>
  <Pattern type="group" Name="Pattern1 Using Face/Group" pixmap=":/images/Hex_Type1.png">
   <Name Value="Hex1" visible="false" key="NAME"/>
   <ElementType type="enum" Value="Hex" key="ELEMTYPE" Index="0"/>
   <MeshSize Value="$MeshSize*0.75 mm" key="MESHSIZE"/>
   <AngularDivisions type="enum" Value="16" key="ANGULAR_DIV" Index="0"/>
   <Hex_Head Value="0"/>
   <Angle type="enum" Value="360 deg" key="ANGLE"/>
   <P_XYZ type="double" Value=" 0 mm,0 mm,0 mm" key="P_X"/>
   <V_XYZ type="double" Value="0 mm,0 mm,1 mm" key="V_X"/>
   <PivotPointLocation type="enum" Value="Above Head" key="HEAD_TYP"/>
   <InputOption type="enum" Value="0" name="InputOption" key="INPUT_OPTION"/>
   <Washer Value="" name="Washer" key="WASHER_FACES" EntityTypes="" ModelIds=""/>
   <Thread Value="" name="Thread" key="THREAD_FACES" EntityTypes="" ModelIds=""/>
   <WasherGroup Value="Washer_VM," name="WasherGroup" key="WASHER_GRP_FACES" EntityTypes="" ModelIds=""/>
   <ThreadGroup Value="Bolt_Thread_VM," name="ThreadGroup" key="THREAD_GRP_FACES" EntityTypes="" ModelIds=""/>
   <Shrinkage Value="0.85" name="Shrinkage for inner dia"/>
   <D2Option type="group" Value="Ratio" name="D2 option" key="D2_OPTION" expand="true"/>
   <OutputWasher Value="WasherGrp" name="OutputWasher" key="OUTPUT_WASHER_FACES" EntityTypes="" ModelIds=""/>
   <OutputThread Value="ThreadGrp" name="OutputThread" key="OUTPUT_THREAD_FACES" EntityTypes="" ModelIds=""/>
   <OutputPretensionFace Value="PretensionGrp" name="OutputPretensionFace" key="OUTPUT_PRETENSION_FACE" EntityTypes="" ModelIds=""/>
   <BoltImport Value="0"/>
   <ScriptLastChild Value="0"/>
   <Parameters>
    <D1 Value="Auto"/>
    <L1 Value="750 mm"/>
    <L3 Value="500 mm"/>
    <L5 Value="Auto"/>
   </Parameters>
  </Pattern>
 </HexBolt>"""


def get_base_template():
    """
    Public user interface for retrieving the template
    """
    return _get_base_template2()


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
        f"pseudo = kwargs.get(\'{pseudo}\', \'{child.attrib.get('Value', '')}\')\n"
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
    sec_str1 += inject_pseudo_value(child)

    sec_str2 = ""
    if child.text is None:
        sec_str2 += PADS4 + f"{child.tag}.text = None\n"

    sec_str3 = append_to_root(child)
    return code_str + sec_str1 + sec_str2 + sec_str3


def parse_sub_elem(code_str, first_child, second_child):
    sec_str = create_sub_elem(first_child, second_child)
    if second_child.attrib.get('Value'):
        sec_str += inject_pseudo_value(second_child)

    if second_child.text and second_child.text.strip():
        sec_str += inject_pseudo_text(second_child)
    return code_str + sec_str


def get_depth_dict(elems, depth_dict=None, depth=0):
    depth_dict = depth_dict or {}
    for elem in elems:
        depth_dict[elem.tag] = (elem, depth)
        if len(elem) != 0:
            get_depth_dict(elem, depth_dict, depth+1)
    return depth_dict


def get_chunk(depth_dict):
    chunks, chunk = [], []
    for tag, (elem, depth) in depth_dict.items():
        if depth == 0 and chunk:
            chunks.append(chunk)
            chunk = []
        chunk.append((elem, depth))
    chunks.append(chunk)  # last chunk
    return chunks


def get_code_str(func_name='get_tree'):
    root = st.session_state.root
    chunks = st.session_state['chunks']

    code_str = f'def {func_name}(**kwargs):\n'
    code_str = parse_root_elem(code_str, next(root.iter()))
    for chunk in chunks:
        for elem, depth in chunk:
            if depth == 0:
                code_str = parse_top_elem(code_str, elem)
            else:
                first_child = chunk[depth-1][0]
                second_child = elem
                code_str = parse_sub_elem(code_str, first_child, second_child)
            code_str += '\n'  # better looking
    code_str += append_return()
    return code_str


def get_print_func(code_str):
    return ''.join(s for s in code_str)


def xml_pretty_print(xml):
    element = ET.XML(xml)
    ET.indent(element)
    return ET.tostring(element, encoding='unicode')


def validate_xml():
    try:
        root = ET.fromstring(st.session_state.input_xml)
        st.session_state['root'] = root
    except xml.etree.ElementTree.ParseError:
        st.error('Not a valid xml format. Please try it again.')
    else:
        depth_dict = get_depth_dict(root)
        chunks = get_chunk(depth_dict)
        st.session_state['chunks'] = chunks

        for chunk in chunks:
            for elem, depth in chunk:
                for k, attrib_value in elem.attrib.items():
                    if k.startswith('Value'):
                        attrib_key = elem.tag + k
                        st.session_state.name_dict[attrib_key] = attrib_value
                if elem.text and elem.text.strip():
                    text_key = elem.tag + 'Text'
                    st.session_state.name_dict[text_key] = elem.text

        st.success('The xml format is valid.')
        st.write(st.session_state.name_dict)
    return st.session_state.name_dict


if __name__ == '__main__':
    st.header('Altair SimLab XML Editor (Experimenting...)')

    if 'name_dict' not in st.session_state:
        st.session_state['name_dict'] = {}

    if 'input_xml' not in st.session_state:
        st.session_state['input_xml'] = ''

    if 'root' not in st.session_state:
        st.session_state['root'] = ''

    if 'chunks' not in st.session_state:
        st.session_state['chunks'] = ''

    func_name = 'get_tree'

    # (0) xml example
    with st.expander("xml example", expanded=True):
        base_template = get_base_template()
        st.code(base_template)

    # (1) Check xml format
    with st.container():
        st.write('(1) Validate xml format')
        xml_placeholder = 'insert xml here'
        input_xml = st.text_area(
            'xml', placeholder=xml_placeholder, height=500)
        if input_xml:
            st.session_state['input_xml'] = input_xml
            validate_xml()

    if input_xml:
        # (2) Input parameters
        with st.container():
            st.write('(2) Input parameters')
            with st.form('form-input-parameters'):
                for k, v in st.session_state.name_dict.items():
                    st.session_state.name_dict[k] = st.text_input(k, v)
                submit = st.form_submit_button()

        # (3) Parsed xml as following
        with st.container():
            if submit:
                st.write(st.session_state.name_dict)
                st.write('(3) Parsed xml as following: ')
                code_str = get_code_str(func_name)
                print_func = get_print_func(code_str)

                exec(code_str)

                rootx = get_tree(**st.session_state.name_dict)
                xm1x = get_template(rootx)
                pp_xmlx = xml_pretty_print(xm1x)
                st.code(pp_xmlx)

                st.write('(4) get_tree: ')
                st.code(print_func)
