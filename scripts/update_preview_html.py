import json
import re

with open('3d_panels/petes_dragon_specs.json', 'r', encoding='utf-8') as f:
    specs = json.load(f)

with open('3d_panels/tpu_panel_preview.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace SPECS = {...};
specs_json_str = json.dumps(specs)
html = re.sub(r'const SPECS = \{.*?\};', f'const SPECS = {specs_json_str};', html)

# Replace description in card
html = re.sub(
    r'<strong style="color:#10b981;">• 16 Outside Eyelets.*?</strong>.*?(?=<br>|</div>)',
    '<strong style="color:#10b981;">• 16 Sleek 45° Outside Eyelets:</strong> 16 compact mounting eyelets with 2.0mm thick walls (ID 2.5mm, OD 6.5mm) tapering cleanly at 45° directly from the shirt-touching back rim (Z = 6.0mm) into the perimeter wall with zero straight protrusion or overhang ledges.',
    html
)

# Replace section 5 of build3DModel in preview HTML
new_tabs_block = """  // 5. 16 Sleek 45° Outside Perimeter Fastener Eyelets (Flush with Backside Z = 4.0mm)
  tabsGroup = new THREE.Group();
  // 45° angled cone tapering from radius 3.25mm down to 1.25mm over 2.0mm height
  const tabConeGeom = new THREE.CylinderGeometry(3.25, 1.25, 2.0, 24);
  tabConeGeom.rotateX(Math.PI / 2);
  const tabHoleGeom = new THREE.CylinderGeometry(1.25, 1.25, 2.2, 24);
  tabHoleGeom.rotateX(Math.PI / 2);
  const tabMat = new THREE.MeshStandardMaterial({ color: 0x059669, roughness: 0.5 });

  if (SPECS.fastener_tabs) {
    SPECS.fastener_tabs.forEach(t => {
      const tabMesh = new THREE.Mesh(tabConeGeom, tabMat);
      tabMesh.position.set(t[0] - cx, t[1] - cy, 3.0); // Z = 2.0 to 4.0mm (flush with back edge)
      tabsGroup.add(tabMesh);
    });
  }
  scene.add(tabsGroup);"""

html = re.sub(
    r'  // 5\. 16.*?\n  scene\.add\(tabsGroup\);',
    new_tabs_block,
    html,
    flags=re.DOTALL
)

with open('3d_panels/tpu_panel_preview.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated 3d_panels/tpu_panel_preview.html successfully!")
