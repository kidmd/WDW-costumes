import zipfile
import xml.etree.ElementTree as ET

with zipfile.ZipFile('3d_panels/tpu_panel_front_multicolor.3mf', 'r') as z:
    xml_data = z.read('3D/3dmodel.model')
    root = ET.fromstring(xml_data)
    ns = '{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}'
    res = root.find(f'{ns}resources')
    objs = res.findall(f'{ns}object')
    print('Objects in resources:')
    for o in objs:
        oid = o.attrib.get('id')
        name = o.attrib.get('name')
        otype = o.attrib.get('type')
        print(f'  id={oid} name={name} type={otype} attribs={o.attrib}')
        comps = o.find(f'{ns}components')
        if comps is not None:
            print('    has components:')
            for c in comps.findall(f'{ns}component'):
                print(f'      component: {c.attrib}')
    build = root.find(f'{ns}build')
    print('\nBuild items:')
    for item in build.findall(f'{ns}item'):
        print(f'  item: {item.attrib}')

    print('\nMetadata/model_settings.config:')
    if 'Metadata/model_settings.config' in z.namelist():
        print(z.read('Metadata/model_settings.config').decode('utf-8'))
    print('\nMetadata/slice_info.config:')
    if 'Metadata/slice_info.config' in z.namelist():
        print(z.read('Metadata/slice_info.config').decode('utf-8'))
