# 🏰 Fairy Light Wire Management Clips (WDW 10K)

Precision snap-fit clips and 90° corner brackets designed for managing external fairy light wires on the WDW 10K running shirts. Engineered specifically for **Rigid PLA / PETG** with tuned cantilever detents and self-centering lead-in ramps.

> [!NOTE]
> **Calibrated for 3.2mm Wire Standard:** All primary straight clips are sized for standard $\approx 3.2\text{ mm}$ jacketed fairy light wiring (inner cavity $\varnothing 3.30\text{ mm}$, snap mouth $2.35\text{ mm}$, reinforced $1.35\text{ mm}$ spring cantilever walls). All STLs default to flat on the build plate at $Z = 0$ with snap mouths pointing straight up toward the nozzle.

---

## 📦 Complete 3D Model Roster (`3d_panels/wire_clips/`)

All STL files are pre-oriented flat on their base at $Z = 0$ for immediate, support-free printing.

| Model File | Description | Dimensions ($W \times L \times H$) | Weight (PLA) | Primary Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **[`clip_corner_90_single.stl`](file:///c:/Users/Kiddi/Desktop/WDW%20costumes/3d_panels/wire_clips/clip_corner_90_single.stl)** | **90° Elbow (Floating, Ribbon-on-Edge)** | $9.10 \times 9.10 \times 5.50\text{ mm}$ | $\approx 0.22\text{g}$ | Pure monolithic $90^\circ$ sweep with vertical $1.40\text{ mm} \times 3.60\text{ mm}$ slot. Seats 3-strand flat fairy light ribbon on edge (vertical stack) so wire bends across thin axis ("the easy way"), preventing copper fatigue or kinking. |
| **[`clip_corner_90_sewable.stl`](file:///c:/Users/Kiddi/Desktop/WDW%20costumes/3d_panels/wire_clips/clip_corner_90_sewable.stl)** | **90° Elbow (Sewable, Ribbon-on-Edge)** | $14.00 \times 14.00 \times 5.50\text{ mm}$ | $\approx 0.27\text{g}$ | Same vertical ribbon 90° elbow plus two 100% clear, unobstructed $\varnothing 2.0\text{ mm}$ stitching eyelets outside the channel wall for needle stitching or safety-pinning to the running shirt. |
| **[`clip_2strand_pyramid_cradle.stl`](file:///c:/Users/Kiddi/Desktop/WDW%20costumes/3d_panels/wire_clips/clip_2strand_pyramid_cradle.stl)** | **2-Strand Pyramid Cradle** | $7.60 \times 8.00 \times 6.27\text{ mm}$ | $\approx 0.25\text{g}$ | **Verified v1 Fit:** Cradles 2 wire strands snugly in the lower lobes with zero slip. |
| **[`clip_2strand_flat.stl`](file:///c:/Users/Kiddi/Desktop/WDW%20costumes/3d_panels/wire_clips/clip_2strand_flat.stl)** | **2-Strand Flat (3.2mm)** | $10.65 \times 8.00 \times 5.01\text{ mm}$ | $\approx 0.28\text{g}$ | Side-by-side hairpin return folds; sits completely flush against running shirt fabric. |
| **[`clip_3strand_flat.stl`](file:///c:/Users/Kiddi/Desktop/WDW%20costumes/3d_panels/wire_clips/clip_3strand_flat.stl)** | **3-Strand Flat (3.2mm)** | $15.30 \times 8.00 \times 5.01\text{ mm}$ | $\approx 0.39\text{g}$ | Flat 3-wire accordion / Z-folds; keeps wiring flat and smooth under bib numbers. |
| **[`clip_2strand_stacked.stl`](file:///c:/Users/Kiddi/Desktop/WDW%20costumes/3d_panels/wire_clips/clip_2strand_stacked.stl)** | **2-Strand Stacked (3.2mm)** | $6.00 \times 8.00 \times 8.55\text{ mm}$ | $\approx 0.28\text{g}$ | Ultra-narrow lateral footprint ($6.0\text{ mm}$); internal waist detent separates bottom and top strands. |
| **[`clip_3strand_bundle.stl`](file:///c:/Users/Kiddi/Desktop/WDW%20costumes/3d_panels/wire_clips/clip_3strand_bundle.stl)** | **3-Strand Pyramid (3.2mm)** | $9.70 \times 8.00 \times 7.93\text{ mm}$ | $\approx 0.36\text{g}$ | Compact triangular cluster sized specifically for three 3.2mm strands; top strand clicks in to lock. |
| **[`wire_gauge_test_comb.stl`](file:///c:/Users/Kiddi/Desktop/WDW%20costumes/3d_panels/wire_clips/wire_gauge_test_comb.stl)** | **Test Gauge Comb** | $36.10 \times 6.00 \times 5.30\text{ mm}$ | $\approx 0.90\text{g}$ | **3-Minute Test Swatch:** 5 stepped slots ($2.6, 2.8, 3.0, 3.2, 3.4\text{ mm}$) to verify physical snap feel. |
| **[`wire_clips_runner_pack.stl`](file:///c:/Users/Kiddi/Desktop/WDW%20costumes/3d_panels/wire_clips/wire_clips_runner_pack.stl)** | **Full Race Day Plate** | $78.30 \times 94.00 \times 8.55\text{ mm}$ | $\approx 8.1\text{g}$ | **25-Piece Plate:** 4x each straight clip (20 clips) + 2x floating 90° + 2x sewable 90° + test comb! |

---

## ⚙️ Slicer & 3D Printing Recommendations

Optimized for **Snapmaker U1** (or Bambu Lab / Prusa / standard FDM) using **100% PLA or PETG**:

1. **Layer Height:** $0.16\text{ mm}$ or $0.20\text{ mm}$.
2. **Walls / Perimeters:** **3 to 4 perimeters** (ensures cantilever arms are 100% solid plastic loops with zero hollow infill).
3. **Infill:** $100\%$ (parts are small enough that 3-4 perimeters naturally fills the solid body).
4. **Supports / Brim:** **None required.** Flat bottom bases provide instant bed adhesion.
5. **Print Orientation:**
   - **Default (Flat on Base):** STLs import pre-oriented with their flat bases on the build plate ($Z = 0$) and snap openings pointing straight up. Zero flipping required.

---

## 🔧 Parametric Customization

### Option 1: OpenSCAD
Open [`wire_clips.scad`](file:///c:/Users/Kiddi/Desktop/WDW%20costumes/3d_panels/wire_clips/wire_clips.scad) in OpenSCAD to adjust wire diameter, bend radius, or clip length using interactive sliders in the Customizer window.

### Option 2: Python Script
Run the automated compiler:
```bash
python scripts/generate_wire_clips.py
```
Rebuilds all models and the multi-pack plate in seconds.
