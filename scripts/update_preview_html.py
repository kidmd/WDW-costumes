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
    r'<strong style="color:#10b981;">• 16 Outside Eyelets:</strong>.*?(?=<br>|</div>)',
    '<strong style="color:#10b981;">• 16 Outside Eyelets (Flush with Back):</strong> 16 mounting eyelets placed on the outside of perimeter rim with 2.0mm thick walls (ID 2.5mm, OD 6.5mm, 2.0mm ear thickness), flush with the back side touching the runner\'s shirt, with 45° self-supporting support gussets underneath.',
    html
)

# Replace section 5 of build3DModel in preview HTML
old_tabs_block = re.search(r'  // 5\. 16 Outside Perimeter Fastener Eyelets.*?\n  scene\.add\(tabsGroup\);', html, re.DOTALL)
if old_tabs_block:
    new_tabs_block = """  // 5. 16 Outside Perimeter Fastener Eyelets (Flush with Backside Z = 4.0mm with 45° Gusset)
  tabsGroup = new THREE.Group();
  const tabShape = new THREE.Shape();
  tabShape.absarc(0, 0, 3.25, 0, Math.PI * 2, false);
  const tabHole = new THREE.Path();
  tabHole.absarc(0, 0, 1.25, 0, Math.PI * 2, true);
  tabShape.holes.push(tabHole);

  // 2.0mm flat ear flush with back edge (Z = 2.0 to 4.0mm)
  const earGeom = new THREE.ExtrudeGeometry(tabShape, { depth: 2.0, bevelEnabled: false });
  const tabMat = new THREE.MeshStandardMaterial({ color: 0x059669, roughness: 0.5 });

  // 45° support gusset underneath (Z = 0.0 to 2.0mm)
  const gussetGeom = new THREE.CylinderGeometry(3.25, 1.25, 2.0, 24);
  gussetGeom.rotateX(Math.PI / 2);

  if (SPECS.fastener_tabs) {
    SPECS.fastener_tabs.forEach(t => {
      const earMesh = new THREE.Mesh(earGeom, tabMat);
      earMesh.position.set(t[0] - cx, t[1] - cy, 2.0); // Z = 2.0 to 4.0mm (flush with back edge)
      tabsGroup.add(earMesh);

      const gussetMesh = new THREE.Mesh(gussetGeom, tabMat);
      gussetMesh.position.set(t[0] - cx, t[1] - cy, 1.0); // Z = 0.0 to 2.0mm
      tabsGroup.add(gussetMesh);
    });
  }
  scene.add(tabsGroup);"""
    html = html.replace(old_tabs_block.group(0), new_tabs_block)
    print("Updated 3D preview tabs geometry with back-flush ears and 45° gussets.")
else:
    print("Could not find old_tabs_block regex match.")

with open('3d_panels/tpu_panel_preview.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated 3d_panels/tpu_panel_preview.html successfully!")
