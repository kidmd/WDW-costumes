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
    r'<strong style="color:#10b981;">• 16.*?Eyelets.*?</strong>.*?(?=<br>|</div>)',
    '<strong style="color:#10b981;">• 16 Pure Round Outside Eyelets:</strong> 16 smooth, 100% circular mounting ears with 2.0mm thick walls (ID 2.5mm, OD 6.5mm) sitting flush with the shirt-touching back rim (Z = 6.0mm) with zero points, zero sharp corners, and zero overhang ledges.',
    html
)

# Replace section 5 of build3DModel in preview HTML
new_tabs_block = """  // 5. 16 Pure Round Outside Perimeter Fastener Eyelets (Flush with Backside Z = 4.0mm)
  tabsGroup = new THREE.Group();
  const tabShape = new THREE.Shape();
  tabShape.absarc(0, 0, 3.25, 0, Math.PI * 2, false);
  const tabHole = new THREE.Path();
  tabHole.absarc(0, 0, 1.25, 0, Math.PI * 2, true);
  tabShape.holes.push(tabHole);

  // 2.0mm tall pure circular cylinder (Z = 2.0 to 4.0mm, top flush with back rim)
  const tabGeom = new THREE.ExtrudeGeometry(tabShape, { depth: 2.0, bevelEnabled: false });
  const tabMat = new THREE.MeshStandardMaterial({ color: 0x059669, roughness: 0.5 });

  if (SPECS.fastener_tabs) {
    SPECS.fastener_tabs.forEach(t => {
      const tabMesh = new THREE.Mesh(tabGeom, tabMat);
      tabMesh.position.set(t[0] - cx, t[1] - cy, 2.0); // Z = 2.0 to 4.0mm (flush with back edge)
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
