# 🏰 Fairy Light Wire Management Clips (WDW 10K)

Precision snap-fit clips designed for managing external fairy light wires folded over themselves outside the chest armor panels on the WDW 10K running shirts. Engineered specifically for **Rigid PLA / PETG** with tuned cantilever detents and self-centering lead-in ramps.

---

## 📦 Included 3D Models

All STL files are located in `3d_panels/wire_clips/` pre-oriented flat on their base at $Z = 0$ for immediate, support-free printing.

| Model File | Type | Dimensions ($W \times L \times H$) | Net Volume / Weight | Best Used For |
| :--- | :--- | :--- | :--- | :--- |
| **[`clip_2strand_flat.stl`](file:///c:/Users/Kiddi/Desktop/WDW%20costumes/3d_panels/wire_clips/clip_2strand_flat.stl)** | 2-Strand Flat | $8.55 \times 8.00 \times 4.15\text{ mm}$ | $161.5\text{ mm}^3$ (~$0.20\text{g}$) | Hairpin return folds; sits completely flush against running shirt fabric. |
| **[`clip_3strand_flat.stl`](file:///c:/Users/Kiddi/Desktop/WDW%20costumes/3d_panels/wire_clips/clip_3strand_flat.stl)** | 3-Strand Flat | $12.20 \times 8.00 \times 4.15\text{ mm}$ | $224.0\text{ mm}^3$ (~$0.28\text{g}$) | 3-wire accordion / Z-folds; keeps wiring flat and smooth under bib numbers. |
| **[`clip_2strand_stacked.stl`](file:///c:/Users/Kiddi/Desktop/WDW%20costumes/3d_panels/wire_clips/clip_2strand_stacked.stl)** | 2-Strand Stacked | $4.90 \times 8.00 \times 6.61\text{ mm}$ | $158.1\text{ mm}^3$ (~$0.20\text{g}$) | Ultra-narrow lateral footprint; internal waist detent separates bottom and top strands. |
| **[`clip_3strand_bundle.stl`](file:///c:/Users/Kiddi/Desktop/WDW%20costumes/3d_panels/wire_clips/clip_3strand_bundle.stl)** | 3-Strand Pyramid | $7.60 \times 8.00 \times 6.27\text{ mm}$ | $197.9\text{ mm}^3$ (~$0.25\text{g}$) | Tight triangular cluster; bottom 2 strands are locked beneath the top snap strand. |
| **[`wire_clips_runner_pack.stl`](file:///c:/Users/Kiddi/Desktop/WDW%20costumes/3d_panels/wire_clips/wire_clips_runner_pack.stl)** | **16-Clip Multi-Pack** | $60.20 \times 47.00 \times 6.61\text{ mm}$ | $2965.6\text{ mm}^3$ (~$3.6\text{g}$) | **Full Race Day Plate:** Prints 4x of each design in a single 15-minute print! |

---

## ⚙️ Slicer & 3D Printing Recommendations

Optimized for **Snapmaker U1** (or Bambu Lab / Prusa / standard FDM) using **100% PLA or PETG**:

1. **Layer Height:** $0.16\text{ mm}$ or $0.20\text{ mm}$.
2. **Walls / Perimeters:** **3 perimeters** (ensures cantilever arms are 100% solid plastic loops with zero hollow infill).
3. **Infill:** $100\%$ (parts are small enough that 3 perimeters naturally fills the solid body).
4. **Supports / Brim:** **None required.** Flat bottom bases provide instant bed adhesion.
5. **Print Orientation:**
   - **Default (Flat on Base):** STLs are oriented with their flat base on the bed ($Z = 0$), providing maximum contact area and zero risk of knocking over.
   - **Upright (Optional for Extra Spring Fatigue Strength):** In slicer or OpenSCAD, rotating the clip $90^\circ$ onto its $8.0\text{ mm}$ end causes the snap cantilever arms to print as continuous XY perimeter loops, giving maximum spring flex against tensile filament forces.

---

## 🔧 Parametric Customization

### Option 1: OpenSCAD
Open [`wire_clips.scad`](file:///c:/Users/Kiddi/Desktop/WDW%20costumes/3d_panels/wire_clips/wire_clips.scad) in OpenSCAD to adjust wire diameter, snap mouth width, or clip length using interactive sliders in the Customizer window.

### Option 2: Python Script
Run the automated compiler:
```bash
python scripts/generate_wire_clips.py
```
This script rebuilds all 4 models and the 16-clip multi-pack plate in seconds.
