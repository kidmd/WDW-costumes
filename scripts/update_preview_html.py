import os

html_path = '3d_panels/dopey_medal/preview_medal.html'
with open(html_path, 'r', encoding='utf-8') as f:
    c = f.read()

# Load the engraved STL as the default monolithic medal
c = c.replace('dopey_photographer_medal_relief.stl', 'dopey_photographer_medal_engraved_back.stl')

# Add lights for the back
back_lights = """  const backLight = new THREE.DirectionalLight(0xffeedd, 2.2);
  backLight.position.set(0, 0, -160);
  scene.add(backLight);

  const backSideLight = new THREE.DirectionalLight(0xffddaa, 1.4);
  backSideLight.position.set(-80, 80, -120);
  scene.add(backSideLight);
"""
if 'backLight' not in c:
    c = c.replace('const rimLight = new THREE.DirectionalLight(0xffdf88, 1.3);', back_lights + '\n  const rimLight = new THREE.DirectionalLight(0xffdf88, 1.3);')

# Add view side buttons
old_btn = '<button class="mode-btn active" id="btn-bronze"'
new_btn = """<div style="font-size: 13px; font-weight: 600; color: var(--gold); text-transform: uppercase; letter-spacing: 0.5px;">View Side</div>
  <div class="btn-row">
    <button class="mode-btn active" id="btn-side-front" onclick="setSide('front')">Front (Dopey)</button>
    <button class="mode-btn" id="btn-side-back" onclick="setSide('back')">Back (Engraved)</button>
  </div>
  <div style="font-size: 13px; font-weight: 600; color: var(--gold); text-transform: uppercase; letter-spacing: 0.5px; margin-top: 4px;">Display Style</div>
  <div class="btn-row">
    <button class="mode-btn active" id="btn-bronze" """

if 'btn-side-back' not in c:
    c = c.replace('<div class="btn-row">\n    <button class="mode-btn active" id="btn-bronze"', new_btn)

# Add setSide JS function
side_func = """
  function setSide(side) {
    document.getElementById('btn-side-front').classList.toggle('active', side === 'front');
    document.getElementById('btn-side-back').classList.toggle('active', side === 'back');
    if (side === 'front') {
      camera.position.set(0, -90, 150);
      controls.target.set(0, 0, 3);
    } else {
      camera.position.set(0, 0, -170);
      controls.target.set(0, 0, -1);
    }
    controls.update();
  }
"""
if 'function setSide' not in c:
    c = c.replace('function resetCamera() {', side_func + '\n  function resetCamera() {')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(c)

print('Updated preview_medal.html successfully!')
