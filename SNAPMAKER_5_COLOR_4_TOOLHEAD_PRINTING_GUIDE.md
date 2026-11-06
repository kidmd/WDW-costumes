# 🎨 Snapmaker Multi-Color Printing Guide: 5 Colors on a 4-Toolhead Machine

This guide details the complete engineering workflow for printing **5-color (or $N+1$ color) models** on a **4-nozzle toolchanger** (such as the **Snapmaker U1** running Klipper) or adapting multi-color jobs on multi-tool setups (like the Snapmaker J1 IDEX).

---

## 1. The Core Engineering Challenge

When a model has 5 distinct colors across its first layers, but the printer physically possesses only 4 independent toolheads:
1. **Toolhead Allocation:** 3 toolheads are dedicated to 3 single colors, while 1 toolhead (e.g., **Toolhead 3 / Nozzle 4**) must do double-duty, printing **Color 4** and **Color 5**.
2. **Slicer Interleaving Issue:** When two parts are assigned to the same extruder in OrcaSlicer / Snapmaker Orca, the slicer optimizes by feature type (`Inner wall` $\rightarrow$ `Outer wall` $\rightarrow$ `Bottom surface`) across the entire plate. It prints walls of Part A, walls of Part B, infill of Part B, infill of Part A. You **cannot** simply pause in between because the two colors are physically interleaved!
3. **The Swap Count Problem:** Printing in a rigid sequence on every layer (e.g., Color 4 then Color 5 on every layer) forces **5 manual filament swaps** across 3 layers.
4. **The Thermal Safety Hazard:** Klipper halts the extruder (`min_extrude_temp = 178°C`) if a trailing cooldown command (`M104 S105`) is misplaced before extrusions finish.

---

## 2. The Solution Architecture

1. **Toolpath Disentanglement:** Partition the shared toolhead's toolpaths into discrete travel-bounded blocks using coordinate boundaries (e.g., spatial $X$ or $Y$ split) so all walls and infill for Part A finish completely before Part B begins.
2. **Alternating "Ping-Pong" Layer Ordering (Cuts Swaps from 5 to 3):**
   * **Layer 1:** Start with Color A $\rightarrow$ **Pause #1** $\rightarrow$ Print Color B (Ends layer with Color B in nozzle).
   * **Layer 2:** *Already loaded with Color B!* Print Color B first $\rightarrow$ **Pause #2** $\rightarrow$ Print Color A (Ends layer with Color A in nozzle).
   * **Layer 3:** *Already loaded with Color A!* Print Color A first $\rightarrow$ **Pause #3** $\rightarrow$ Print Color B (Ends layer with Color B in nozzle).
   * Toolhead 3 is now 100% finished for the rest of the print!
3. **Hardware Pause, Thermal Protection & Prime Tower Visit:**
   * Inject `M400` (buffer clear), `M117` (on-screen LCD message), `PAUSE` (Klipper parking macro).
   * Upon resume: enforce `M104 S[temp]` and `M109 S[temp]` (wait for target temperature).
   * Immediately detour to the **Prime Tower** ($X \in [220, 242]\text{ mm}$) to extrude a $22\text{ mm}$ sacrificial priming bead before traveling to the cosmetic part. This restores melt-chamber pressure and prevents first-millimeter under-extrusion or travel ooze.
4. **Mid-Print Tool Re-purposing (e.g., Clear Backing Diffuser):** Before higher layers start (e.g., Layer 4), pause a retired toolhead (e.g., Toolhead 2 / Nozzle 3) to swap from its first-layer color to Clear PETG.

---

## 3. Slicer Setup in Snapmaker Orca

1. **Keep the Standard 4-Extruder Profile:**
   Snapmaker Orca locks the U1 machine profile to 4 nozzles. Do not attempt to add a 5th extruder in the profile settings.
2. **Assign Parts in the Objects List:**
   * Go to **Objects** tab on the left.
   * Assign Color 1 $\rightarrow$ Nozzle 1 (`T0`)
   * Assign Color 2 $\rightarrow$ Nozzle 2 (`T1`)
   * Assign Color 3 $\rightarrow$ Nozzle 3 (`T2`)
   * Assign **both Color 4 (Part A) and Color 5 (Part B)** $\rightarrow$ **Nozzle 4 (`T3`)**.
3. **Pairing Strategy for the Shared Nozzle:**
   * Pick two parts that have a physical gap between them on the bed.
   * Pick a color that ends early (e.g., bottom-layer detail like tie/lips or accents) to share with a color that finishes on the same layer.
4. **Slice & Export:**
   * Click **Slice plate**.
   * Click **Export G-code file** (e.g. `model_raw.gcode`).

---

## 4. Automated Python G-Code Post-Processor

Save and run this script to parse any raw G-code, disentangle the dual-color toolpaths, apply ping-pong ordering, and inject safe pauses.

```python
#!/usr/bin/env python3
"""
Snapmaker Multi-Color Toolpath Disentangler & Pause Injector
Splits a shared toolhead into two distinct colors with ping-pong ordering.
"""
import re
import sys

def process_gcode(
    input_path,
    output_path,
    shared_tool=3,           # T3 = Nozzle 4 (0-indexed)
    split_coord='X',         # 'X' or 'Y' coordinate to split on
    split_threshold=142.0,   # Boundary threshold in mm
    part_a_name="Tie & Lips",
    part_b_name="Shell & Glasses",
    target_temp=255,
    num_layers=3,            # Number of multi-color layers
    layer_4_swap_tool=None,  # e.g., 2 for T2 (Nozzle 3) clear backing swap
    layer_4_swap_name="Clear PETG"
):
    with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    print(f"Loaded {len(lines)} lines from {input_path}")

    # Track layer ranges for the shared tool
    tool_marker = f"T{shared_tool}"
    layer_t3_ranges = {}
    curr_l = 0
    in_shared_tool = False
    range_start = None

    for idx, l in enumerate(lines):
        if 'CURRENT_LAYER=' in l:
            m = re.search(r'CURRENT_LAYER=(\d+)', l)
            if m:
                curr_l = int(m.group(1))
        
        # Tool change detection
        if l.strip().startswith('; Change Tool') or re.match(r'^T\d', l.strip()):
            m = re.search(r'T(\d+)', l)
            if m:
                t_num = int(m.group(1))
                if t_num == shared_tool and not in_shared_tool:
                    in_shared_tool = True
                    range_start = idx
                elif t_num != shared_tool and in_shared_tool:
                    in_shared_tool = False
                    if curr_l <= num_layers:
                        layer_t3_ranges[curr_l] = (range_start, idx - 1)

    print(f"Detected shared tool {tool_marker} on layers: {list(layer_t3_ranges.keys())}")

    def reorder_layer(s_idx, e_idx, order, l_num):
        # Extract blocks based on high-speed travel moves (F30000)
        travels = [i for i in range(s_idx, e_idx) if 'F30000' in lines[i] and 'G1' in lines[i] and 'E' not in lines[i]]
        blocks = []
        prev = s_idx
        for t in travels:
            if t > prev:
                blocks.append((prev, t - 1))
                prev = t
        blocks.append((prev, e_idx))

        setup_blocks, part_a_blocks, part_b_blocks, prime_blocks, cooldown_blocks = [], [], [], [], []
        first_ext = False

        for bs, be in blocks:
            bl = lines[bs:be+1]
            coords = []
            is_prime = False
            for line in bl:
                if ';TYPE:Prime tower' in line:
                    is_prime = True
                m = re.search(r'G1\s+.*' + split_coord + r'([0-9.]+).*E([0-9.-]+)', line)
                if m:
                    coords.append(float(m.group(1)))

            if is_prime or (coords and min(coords) > 205.0):
                first_ext = True
                prime_blocks.append(bl)
            elif not coords:
                if not first_ext:
                    setup_blocks.append(bl)
                else:
                    cooldown_blocks.append(bl)
            elif (min(coords) > split_threshold and split_coord == 'X'):
                first_ext = True
                part_a_blocks.append(bl)
            else:
                first_ext = True
                part_b_blocks.append(bl)

        pause_a_to_b = [
            f"\n; === PAUSE: SWAP T{shared_tool} TO [{part_b_name}] ===\n",
            "M400\n",
            f"M117 Load {part_b_name} on T{shared_tool}\n",
            "PAUSE\n",
            f"M104 S{target_temp} T{shared_tool}\n",
            f"M109 S{target_temp} T{shared_tool}\n\n"
        ]

        pause_b_to_a = [
            f"\n; === PAUSE: SWAP T{shared_tool} TO [{part_a_name}] ===\n",
            "M400\n",
            f"M117 Load {part_a_name} on T{shared_tool}\n",
            "PAUSE\n",
            f"M104 S{target_temp} T{shared_tool}\n",
            f"M109 S{target_temp} T{shared_tool}\n\n"
        ]

        out = []
        for b in setup_blocks:
            out.extend(b)
        out.append(f"M104 S{target_temp} T{shared_tool}\n")
        out.append(f"M109 S{target_temp} T{shared_tool}\n")

        if order == 'A_FIRST':
            for b in part_a_blocks: out.extend(b)
            out.extend(pause_a_to_b)
            for b in part_b_blocks: out.extend(b)
        else:
            for b in part_b_blocks: out.extend(b)
            out.extend(pause_b_to_a)
            for b in part_a_blocks: out.extend(b)

        for b in prime_blocks: out.extend(b)
        for b in cooldown_blocks: out.extend(b)
        return out

    # Assemble complete modified G-code
    output = []
    last_idx = 0

    for l_num in sorted(layer_t3_ranges.keys()):
        start, end = layer_t3_ranges[l_num]
        output.extend(lines[last_idx:start])
        # Alternating ping-pong: L1 = A_FIRST, L2 = B_FIRST, L3 = A_FIRST
        order = 'A_FIRST' if (l_num % 2 == 1) else 'B_FIRST'
        output.extend(reorder_layer(start, end, order, l_num))
        last_idx = end + 1

    # Check for layer 4 tool swap
    if layer_4_swap_tool is not None:
        l4_tool_marker = f"T{layer_4_swap_tool}"
        # Search for first pickup of this tool after layer 3
        for idx in range(last_idx, len(lines)):
            if lines[idx].strip() == l4_tool_marker:
                output.extend(lines[last_idx:idx+1])
                output.append(f"\n; === PAUSE: SWAP T{layer_4_swap_tool} TO [{layer_4_swap_name}] ===\n")
                output.append("M400\n")
                output.append(f"M117 Load {layer_4_swap_name} on T{layer_4_swap_tool}\n")
                output.append("PAUSE\n")
                output.append(f"M104 S{target_temp} T{layer_4_swap_tool}\n")
                output.append(f"M109 S{target_temp} T{layer_4_swap_tool}\n\n")
                last_idx = idx + 1
                break

    output.extend(lines[last_idx:])

    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(output)
    print(f"Successfully wrote {len(output)} lines to {output_path}")

if __name__ == "__main__":
    # Example usage:
    # python process_gcode.py input.gcode output.gcode
    pass
```

---

## 5. Thermal Verification & Quality Checks

Before running modified G-code, verify with an automated simulation check:
1. **Zero Cooldowns During Active Extrusion:** Ensure no `M104 S105` command precedes positive `G1 ... E...` extrusion commands for the active tool.
2. **Temperature Reheat Enforced:** After every `PAUSE`, `M109 S[temp]` must be present to guarantee the nozzle reheats to target before resuming print movements.
3. **Bed Temperature Preservation:** Verify `M140` (bed target) or `M190` never sets bed temperature to zero mid-print.

---

## 6. Machine Choreography & Race-Day Operation

When running the print on the Snapmaker U1:

1. **Initial Toolhead Loading:**
   * **T0 (Nozzle 1):** Color 1
   * **T1 (Nozzle 2):** Color 2
   * **T2 (Nozzle 3):** Color 3
   * **T3 (Nozzle 4):** **Color A** (the color scheduled to print first on Layer 1)
2. **Handling the Pause:**
   * The U1 automatically executes `PAUSE`, parks Toolhead 3 at the purge/dock location, and displays the `M117` message on the touchscreen.
   * On the touchscreen, tap **Unload**, remove Color A, insert Color B, and tap **Load / Extrude**.
   * **Visual Purge Check:** Inspect the purge noodle coming out of the nozzle into the chute until it is 100% pure Color B with zero color contamination.
   * **Clean the Nozzle:** Use brass tweezers or a brush to clear away any tip curl or stringing.
   * Tap **Resume**.
3. **Ping-Pong Execution:**
   * On Layer 2, do not touch the printer when Layer 2 starts—it will automatically print Color B first, then pause for Color A.
   * On Layer 3, it automatically prints Color A first, then pauses for Color B.
   * Before Layer 4, Toolhead 2 parks for the Clear Backing swap.
4. **Post-Layer 4:**
   * The rest of the print finishes on full autopilot with zero further manual intervention.
