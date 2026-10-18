import os
import sys
import subprocess
import shutil
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INCLUDE_DIR = os.path.join(BASE_DIR, "include")
FIRMWARE_DIR = os.path.join(BASE_DIR, "firmware")
PIO_BUILD_DIR = os.path.join(BASE_DIR, ".pio", "build", "esp32dev")

FLOATS = [
    {"id": 1, "name": "The Train", "role": "LEADER", "tag": "CASEY JR."},
    {"id": 2, "name": "The Title Drum", "role": "FOLLOWER", "tag": "THE DRUM"},
    {"id": 3, "name": "The Spinning Turtle", "role": "FOLLOWER", "tag": "TURTLE"},
    {"id": 4, "name": "The Spinning Snail", "role": "FOLLOWER", "tag": "SNAIL"},
    {"id": 5, "name": "Pirate Ship", "role": "FOLLOWER", "tag": "PIRATE"},
    {"id": 6, "name": "Pete's Dragon", "role": "FOLLOWER", "tag": "ELLIOTT"},
    {"id": 7, "name": "To Honor America", "role": "FOLLOWER", "tag": "FLAG & EAGLE"},
]

def sync_fleet_palettes():
    """
    Synchronizes DEFAULT_FLOAT_PALETTES and 16x16 Matrix mappings in include/fleet_palettes.h
    and arduino/MSEP_Costume/fleet_palettes.h from active presets in presets/fleet_lineup.json.
    Ensures that any LED moves, newly sampled background colors, 16x16 matrix settings, or preset updates
    are 100% baked into the firmware for all 7 floats.
    """
    lineup_file = os.path.join(BASE_DIR, "presets", "fleet_lineup.json")
    if not os.path.exists(lineup_file):
        print("[WARN] presets/fleet_lineup.json not found; skipping fleet palette sync.")
        return False

    try:
        with open(lineup_file, "r", encoding="utf-8") as f:
            lineup = json.load(f)
    except Exception as e:
        print(f"[WARN] Failed to read fleet_lineup.json: {e}")
        return False

    palettes_by_float = {}
    is_matrix_by_float = {}
    active_count_by_float = {}
    matrix_indices_by_float = {}

    for flt in lineup:
        slot = flt.get("slot", 0)
        float_id = slot + 1
        preset_rel = flt.get("preset", "").replace("server:", "")
        preset_path = os.path.join(BASE_DIR, "presets", preset_rel)
        colors = []
        is_mat = 0
        act_count = 100
        mat_indices = [i for i in range(100)]

        if os.path.exists(preset_path):
            try:
                with open(preset_path, "r", encoding="utf-8") as pf:
                    p_data = json.load(pf)

                mat_active = bool(p_data.get("btfMatrix16x16Active", False) or p_data.get("matrix_16x16_mode", False))
                win_leds = p_data.get("matrixWindowedLeds", p_data.get("matrix_windowed_leds", []))
                glow_leds = p_data.get("matrixBacklightLeds", p_data.get("matrix_backlight_leds", []))

                if mat_active and (len(win_leds) > 0 or len(glow_leds) > 0):
                    is_mat = 1
                    combined = sorted(win_leds + glow_leds, key=lambda item: int(item.get("id", 0)))
                    act_count = min(256, len(combined))
                    mat_indices = []
                    for i in range(100):
                        entry = combined[i % len(combined)]
                        c = entry.get("color", {})
                        r = int(c.get("r", 255))
                        g = int(c.get("g", 183))
                        b = int(c.get("b", 3))
                        colors.append((r, g, b))
                        if i < len(combined):
                            mat_indices.append(max(0, min(255, int(entry.get("id", i)))))
                        else:
                            mat_indices.append(255)
                    print(f"[MATRIX 16x16] Float {float_id} ({flt.get('name', '')}): {len(win_leds)} Windowed + {len(glow_leds)} Backlit = {act_count} active LEDs.")
                else:
                    leds = p_data.get("leds", [])
                    if leds:
                        act_count = min(100, len(leds))
                        for i in range(100):
                            led_entry = leds[i % len(leds)]
                            c = led_entry.get("color", {})
                            r = int(c.get("r", 255))
                            g = int(c.get("g", 183))
                            b = int(c.get("b", 3))
                            colors.append((r, g, b))
            except Exception as pe:
                print(f"[WARN] Error reading {preset_rel} for Float {float_id}: {pe}")

        if len(colors) < 100:
            colors = [(255, 183, 3)] * 100
        if len(mat_indices) < 100:
            mat_indices = [i % 256 for i in range(100)]

        palettes_by_float[float_id] = colors
        is_matrix_by_float[float_id] = is_mat
        active_count_by_float[float_id] = act_count
        matrix_indices_by_float[float_id] = mat_indices

    lines = [
        "#ifndef FLEET_PALETTES_H",
        "#define FLEET_PALETTES_H",
        "",
        "#include <FastLED.h>",
        "",
        "#define HAS_DEFAULT_FLOAT_PALETTES 1",
        "#define HAS_FLEET_MATRIX_CONFIG 1",
        "",
        "// 16x16 BTF Matrix Mode flags & active LED counts per float (Floats 1..7 -> indices 0..6)",
        "const uint8_t PROGMEM FLOAT_IS_MATRIX_16X16[7] = { " + ", ".join(str(is_matrix_by_float.get(fid, 0)) for fid in range(1, 8)) + " };",
        "const uint8_t PROGMEM FLOAT_ACTIVE_LED_COUNT[7] = { " + ", ".join(str(active_count_by_float.get(fid, 100)) for fid in range(1, 8)) + " };",
        "",
        "// Physical 16x16 serpentine matrix indices (0..255) for active Windowed + Backlit LEDs",
        "const uint8_t PROGMEM FLOAT_MATRIX_INDICES[7][100] = {"
    ]

    for fid in range(1, 8):
        flt_meta = next((f for f in FLOATS if f["id"] == fid), {"name": f"Float {fid}"})
        m_idxs = matrix_indices_by_float.get(fid, [i for i in range(100)])
        idx_str = ", ".join(str(v) for v in m_idxs[:100])
        close_comma = "," if fid < 7 else ""
        lines.append(f"    {{ {idx_str} }}{close_comma} // Float {fid}: {flt_meta['name']}")

    lines.extend([
        "};",
        "",
        "// Authentic default background graphic colors for all 7 floats (100 LEDs each)",
        "// Automatically synchronized from active fleet presets by build_fleet_binaries.py",
        "// Used for 📸 Castle Photo Mode and default float palettes",
        "const CRGB PROGMEM DEFAULT_FLOAT_PALETTES[7][100] = {"
    ])

    for fid in range(1, 8):
        flt_meta = next((f for f in FLOATS if f["id"] == fid), {"name": f"Float {fid}"})
        lines.append(f"    // Float {fid}: {flt_meta['name']}")
        lines.append("    {")
        f_colors = palettes_by_float.get(fid, [(255, 183, 3)] * 100)
        for i, (r, g, b) in enumerate(f_colors):
            comma = "," if i < 99 else ""
            lines.append(f"        CRGB({r}, {g}, {b}){comma}")
        close_comma = "," if fid < 7 else ""
        lines.append(f"    }}{close_comma}")

    lines.append("};")
    lines.append("")
    lines.append("#endif // FLEET_PALETTES_H")
    lines.append("")

    header_content = "\n".join(lines)

    target_paths = [
        os.path.join(INCLUDE_DIR, "fleet_palettes.h"),
        os.path.join(BASE_DIR, "arduino", "MSEP_Costume", "fleet_palettes.h")
    ]

    for tp in target_paths:
        os.makedirs(os.path.dirname(tp), exist_ok=True)
        with open(tp, "w", encoding="utf-8") as out_f:
            out_f.write(header_content)

    print(f"[OK] Synchronized fleet_palettes.h for all 7 floats from active presets.")
    return True

def write_float_config(float_id, fleet_build=True):
    os.makedirs(INCLUDE_DIR, exist_ok=True)
    config_file = os.path.join(INCLUDE_DIR, "float_config.h")
    fleet_def = "\n#define FLEET_BUILD 1\n" if fleet_build else "\n"
    content = f"""#ifndef FLOAT_CONFIG_H
#define FLOAT_CONFIG_H

// Auto-generated dedicated float identity
#ifndef COMPILED_FLOAT_ID
#define COMPILED_FLOAT_ID {float_id}
#endif
{fleet_def}
#endif // FLOAT_CONFIG_H
"""
    with open(config_file, "w", encoding="utf-8") as f:
        f.write(content)

def build_binary(float_id=0):
    write_float_config(float_id, fleet_build=True)
    cmd = [sys.executable, "-m", "platformio", "run"]
    res = subprocess.run(cmd, cwd=BASE_DIR, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[ERROR] Build failed for Float {float_id}:\n{res.stderr or res.stdout}")
        return False
    
    os.makedirs(FIRMWARE_DIR, exist_ok=True)
    # Copy bootloader and partitions
    src_bl = os.path.join(PIO_BUILD_DIR, "bootloader.bin")
    src_pt = os.path.join(PIO_BUILD_DIR, "partitions.bin")
    src_fw = os.path.join(PIO_BUILD_DIR, "firmware.bin")

    if os.path.exists(src_bl):
        shutil.copy2(src_bl, os.path.join(FIRMWARE_DIR, "bootloader.bin"))
    if os.path.exists(src_pt):
        shutil.copy2(src_pt, os.path.join(FIRMWARE_DIR, "partitions.bin"))
    
    bin_name = f"firmware_float{float_id}.bin" if float_id > 0 else "firmware.bin"
    target_fw = os.path.join(FIRMWARE_DIR, bin_name)
    shutil.copy2(src_fw, target_fw)

    # Manifest
    float_name = "Generic / Auto"
    for f in FLOATS:
        if f["id"] == float_id:
            float_name = f"{f['name']} ({f['role']})"
            break

    manifest = {
        "name": f"MSEP Costume - {float_name}",
        "version": "1.0.0",
        "new_install_prompt_erase": False,
        "builds": [
            {
                "chipFamily": "ESP32",
                "parts": [
                    {"path": "bootloader.bin", "offset": 4096},
                    {"path": "partitions.bin", "offset": 32768},
                    {"path": bin_name, "offset": 65536}
                ]
            }
        ]
    }
    manifest_name = f"manifest_float{float_id}.json" if float_id > 0 else "manifest.json"
    manifest_path = os.path.join(FIRMWARE_DIR, manifest_name)
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"[OK] Successfully built Float {float_id} -> {bin_name} & {manifest_name}")
    return True

def build_all():
    print("==================================================")
    print(" Building MSEP Costume ROM Binaries for All Floats")
    print("==================================================")
    
    # 1. Synchronize fleet_palettes.h from active presets
    sync_fleet_palettes()

    # 2. Build Generic and all 7 dedicated float binaries
    build_binary(0)
    for flt in FLOATS:
        build_binary(flt["id"])
        
    # Reset float_config.h back to 0 (generic/NVS mode) after dedicated builds complete
    write_float_config(0, fleet_build=False)

    print("==================================================")
    print(" Finished building all 7 float ROM binaries!")
    print("==================================================")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        fid = int(sys.argv[1])
        if fid == 0 or any(f["id"] == fid for f in FLOATS):
            sync_fleet_palettes()
            build_binary(fid)
            write_float_config(0, fleet_build=False)
    else:
        build_all()

