import os

with open('PROJECT_PROGRESS.md', 'r', encoding='utf-8') as f:
    text = f.read()

target = '## Progress Log\n\n### 2026-11-04 17:00: Snapmaker Orca / OrcaSlicer 3MF XML Compliance & Project Compatibility Fix'

replacement = '''## Progress Log

### 2026-11-04 17:50: Float 7 (To Honor America) Front Banner Drape 6 Red Stripes Refinement
- **Front Banner Drape Stripe Harmonization (6 Red & 5 White Stripes):**
  - **The Request & Visual Balance:** The undulating middle and rear flag waves of the *To Honor America* grand finale unit have six red stripes. However, the leading front drape bearing the `"TO HONOR AMERICA"` swallowtail banner originally only featured four broad red stripes.
  - **Geometric Reconstruction:** Rescaled the front drape from 7 stripes (4 red, 3 white) to 11 stripes (6 red, 5 white), perfectly aligning with the scale of the stripes across the rest of the float (~27–34 px stripe width, separated by ~6–7 px black stained-glass leading).
  - **Symmetric Scallop Distribution:**
    - Left scallop (flaring to the nose): 5 stripes (Red 1, White 1, Red 2, White 2, Red 3).
    - Center crease / V-notch apex: Separator line 5 follows the continuous quadratic crease curve ($x = 259, y = 740$).
    - Right scallop (transitioning to side skirt): 6 stripes (White 3, Red 4, White 4, Red 5, White 5, Red 6).
    - Top rolled edge & banner: 100% vertical alignment passing behind the horizontal swallowtail banner.
- **Safety Backup & Strict Multi-Material Slicing Verification:**
  - Preserved the original 4-stripe version in `assets/backup_honor_america_4stripes/`, `assets/to_honor_america_4stripes_backup.png`, and `simulator/assets/to_honor_america_4stripes_backup.png`.
  - Verified 100% discrete 4-color palette compliance (560,256 foreground px, 0 anti-aliased edge artifacts):
    1. **Black (`#11161d`):** 230,413 px (41.13%)
    2. **White (`#ffffff`):** 150,084 px (26.79%)
    3. **Red (`#d81d17`):** 96,199 px (17.17%)
    4. **Blue (`#1f4a7d`):** 83,560 px (14.91%)
- **Production Asset & Simulator Synchronization:**
  - Deployed to `assets/honor_america_eagle.png`, `assets/to_honor_america.png`, `simulator/assets/honor_america_eagle.png`, `simulator/assets/to_honor_america.png`, and `scripts/honor_america_4color_clean.png`.
  - Bumped `simulator/app.js` cache buster to `?v=20261104_honor_america_6stripes`.

### 2026-11-04 17:00: Snapmaker Orca / OrcaSlicer 3MF XML Compliance & Project Compatibility Fix'''

assert target in text, 'target not in text'
text = text.replace(target, replacement, 1)

# Remove the accidental second '## Progress Log\n\n' if present
second_target = '## Progress Log\n\n### 2026-11-04 16:15:'
if second_target in text:
    text = text.replace(second_target, '### 2026-11-04 16:15:', 1)

with open('PROJECT_PROGRESS.md', 'w', encoding='utf-8') as f:
    f.write(text)

print('PROJECT_PROGRESS.md updated cleanly!')
