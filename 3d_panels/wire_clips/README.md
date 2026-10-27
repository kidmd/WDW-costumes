# 🏰 Fairy Light Wire Management Clips (WDW 10K)

Precision snap-fit clips designed for managing external fairy light wires folded over themselves outside the chest armor panels on the WDW 10K running shirts. Engineered specifically for **Rigid PLA / PETG** with tuned cantilever detents and self-centering lead-in ramps.

> [!NOTE]
> **Resized for ~3.0mm Wire & Auto-Oriented:** Sized for standard jacketed fairy light wiring ($\approx 2.8\text{ mm}$ to $3.05\text{ mm}$ OD, cavity $\varnothing 3.10\text{ mm}$, neck $2.20\text{ mm}$). All STLs default to flat on the build plate with the bases at $Z = 0$ and the snap mouths pointing straight up toward the nozzle.

---

## 📦 Included 3D Models

All STL files are located in `3d_panels/wire_clips/` pre-oriented flat on their base at $Z = 0$ for immediate, support-free printing.

| Model File | Type | Dimensions ($W \times L \times H$) | Net Volume / Weight | Best Used For |
| :--- | :--- | :--- | :--- | :--- |
| **[`clip_2strand_flat.stl`](file:///c:/Users/Kiddi/Desktop/WDW%20costumes/3d_panels/wire_clips/clip_2strand_flat.stl)** | 2-Strand Flat | $10.10 \times 8.00 \times 4.80\text{ mm}$ | $210.6\text{ mm}^3$ (~$0.26\text{g}$) | Hairpin return folds; sits completely flush against running shirt fabric. |
| **[`clip_3strand_flat.stl`](file:///c:/Users/Kiddi/Desktop/WDW%20costumes/3d_panels/wire_clips/clip_3strand_flat.stl)** | 3-Strand Flat | $14.50 \times 8.00 \times 4.80\text{ mm}$ | $292.3\text{ mm}^3$ (~$0.36\text{g}$) | 3-wire accordion / Z-folds; keeps wiring flat and smooth under bib numbers. |
| **[`clip_2strand_stacked.stl`](file:///c:/Users/Kiddi/Desktop/WDW%20costumes/3d_panels/wire_clips/clip_2strand_stacked.stl)** | 2-Strand Stacked | $5.70 \times 8.00 \times 8.14\text{ mm}$ | $210.3\text{ mm}^3$ (~$0.26\text{g}$) | Ultra-narrow lateral footprint; internal waist detent separates bottom and top strands. |
| **[`clip_3strand_bundle.stl`](file:///c:/Users/Kiddi/Desktop/WDW%20costumes/3d_panels/wire_clips/clip_3strand_bundle.stl)** | 3-Strand Pyramid | $9.20 \times 8.00 \times 7.55\text{ mm}$ | $269.4\text{ mm}^3$ (~$0.34\text{g}$) | Tight triangular cluster; bottom 2 strands seat cleanly, top strand snaps down to lock. |
| **[`wire_gauge_test_comb.stl`](file:///c:/Users/Kiddi/Desktop/WDW%20costumes/3d_panels/wire_clips/wire_gauge_test_comb.stl)** | **Test Gauge Comb** | $36.10 \times 6.00 \times 5.30\text{ mm}$ | $734.6\text{ mm}^3$ (~$0.9\text{g}$) | **3-Minute Test Swatch:** 5 stepped slots ($2.6, 2.8, 3.0, 3.2, 3.4\text{ mm}$) to verify test fit! |
| **[`wire_clips_runner_pack.stl`](file:///c:/Users/Kiddi/Desktop/WDW%20costumes/3d_panels/wire_clips/wire_clips_runner_pack.stl)** | **Full Print Plate** | $74.50 \times 62.00 \times 8.14\text{ mm}$ | $4664.8\text{ mm}^3$ (~$5.8\text{g}$) | **Complete Race Day Plate:** Prints 4x of each clip (16 clips) + 1 test comb in ~20 minutes! |

---

## ⚙️ Slicer & 3D Printing Recommendations

Optimized for **Snapmaker U1** (or Bambu Lab / Prusa / standard FDM) using **100% PLA or PETG**:

1. **Layer Height:** $0.16\text{ mm}$ or $0.20\text{ mm}$.
2. **Walls / Perimeters:** **3 perimeters** (ensures cantilever arms are 100% solid plastic loops with zero hollow infill).
3. **Infill:** $100\%$ (parts are small enough that 3 perimeters naturally fills the solid body).
4. **Supports / Brim:** **None required.** Flat bottom bases provide instant bed adhesion.
5. **Print Orientation:**
   - **Default (Flat on Base):** STLs import pre-oriented with their flat bases on the build plate ($Z = 0$) and snap openings pointing straight up. Zero flipping required.

---

## 🔧 Parametric Customization

### Option 1: OpenSCAD
Open [`wire_clips.scad`](file:///c:/Users/Kiddi/Desktop/WDW%20costumes/3d_panels/wire_clips/wire_clips.scad) in OpenSCAD to adjust wire diameter, snap mouth width, or clip length using interactive sliders in the Customizer window.

### Option 2: Python Script
Run the automated compiler:
```bash
python scripts/generate_wire_clips.py
```
This script rebuilds all 4 models, the test gauge comb, and the multi-pack plate in seconds.
