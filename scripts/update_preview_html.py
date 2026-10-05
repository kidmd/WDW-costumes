import json
import re

with open('3d_panels/petes_dragon_specs.json', 'r', encoding='utf-8') as f:
    specs = json.load(f)

with open('3d_panels/tpu_panel_preview.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace SPECS = {...};
specs_json_str = json.dumps(specs)
html = re.sub(r'const SPECS = \{.*?\};', f'const SPECS = {specs_json_str};', html)

# Replace the text descriptions
html = html.replace(
    'Backside Rim Fastener Tabs (16)',
    'Outside Perimeter Eyelets (16, 2mm walls)'
)
html = html.replace(
    '16 Border Eyelets',
    '16 Outside Eyelets (2mm walls)'
)
html = html.replace(
    '<strong style="color:#10b981;">• Backside Eyelets:</strong> 16 tabs connected to inside rim (front face is 100% puncture-free).',
    '<strong style="color:#10b981;">• 16 Outside Eyelets:</strong> 16 mounting eyelets placed on the outside of perimeter rim with 2.0mm thick walls (ID 2.5mm, OD 6.5mm, 4.0mm height).'
)

# Fix tabsGroup in build3DModel()
# Replace section 5 of build3DModel:
old_tab_section = """  // 5. 16 Backside Rim Fastener Eyelets (Ear tabs connected to inner rim wall)
  tabsGroup = new THREE.Group();
  const tabGeom = new THREE.CylinderGeometry(3.0, 3.0, 3.0, 16);
  const tabHoleGeom = new THREE.CylinderGeometry(1.25, 1.25, 3.2, 16);
  const tabMat = new THREE.MeshStandardMaterial({ color: 0x059669, roughness: 0.5 });

  if (SPECS.fastener_tabs) {
    SPECS.fastener_tabs.forEach(t => {
      const tabMesh = new THREE.Mesh(tabGeom, tabMat);
      tabMesh.rotation.x = Math.PI / 2;
      tabMesh.position.set(t[0] - cx, t[1] - cy, 1.5);
      tabsGroup.add(tabMesh);
    });
  }
  scene.add(tabsGroup);"""

new_tab_section = """  // 5. 16 Outside Perimeter Fastener Eyelets (2.0mm thick walls, OD 6.5mm, H 4.0mm)
  tabsGroup = new THREE.Group();
  const tabShape = new THREE.Shape();
  tabShape.absarc(0, 0, 3.25, 0, Math.PI * 2, false);
  const tabHole = new THREE.Path();
  tabHole.absarc(0, 0, 1.25, 0, Math.PI * 2, true);
  tabShape.holes.push(tabHole);

  const tabGeom = new THREE.ExtrudeGeometry(tabShape, { depth: 4.0, bevelEnabled: false });
  const tabMat = new THREE.MeshStandardMaterial({ color: 0x059669, roughness: 0.5 });

  if (SPECS.fastener_tabs) {
    SPECS.fastener_tabs.forEach(t => {
      const tabMesh = new THREE.Mesh(tabGeom, tabMat);
      tabMesh.position.set(t[0] - cx, t[1] - cy, -2.0);
      tabsGroup.add(tabMesh);
    });
  }
  scene.add(tabsGroup);"""

if old_tab_section in html:
    html = html.replace(old_tab_section, new_tab_section)
    print("Replaced section 5 tabs successfully.")
else:
    print("Could not find exact old_tab_section, will check regex.")

# Remove duplicate tabsGroup re-definition at line ~784
old_dup_tab = """  // 10. Clean Perimeter Fastener Tabs (16 strictly along border)
  tabsGroup = new THREE.Group();
  const tabGeom = new THREE.RingGeometry(1.1, 2.4, 16);
  const tabMat = new THREE.MeshBasicMaterial({ color: 0x0284c7, side: THREE.DoubleSide });
  SPECS.fastener_tabs.forEach(f => {
    const ring = new THREE.Mesh(tabGeom, tabMat);
    ring.position.set(f[0] - cx, f[1] - cy, 1.15);
    tabsGroup.add(ring);
  });
  scene.add(tabsGroup);"""

if old_dup_tab in html:
    html = html.replace(old_dup_tab, "  // (Eyelets rendered as 3D extruded solid cylinders above)")
    print("Removed duplicate tabsGroup override successfully.")

with open('3d_panels/tpu_panel_preview.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated 3d_panels/tpu_panel_preview.html successfully!")
