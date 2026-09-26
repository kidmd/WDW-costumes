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
    {"id": 3, "name": "Cinderella's Coach", "role": "FOLLOWER", "tag": "CINDERELLA"},
    {"id": 4, "name": "Peter Pan's Pirate Ship", "role": "FOLLOWER", "tag": "PETER PAN"},
    {"id": 5, "name": "Dumbo the Flying Elephant", "role": "FOLLOWER", "tag": "DUMBO"},
    {"id": 6, "name": "Pete's Dragon", "role": "FOLLOWER", "tag": "ELLIOTT"},
    {"id": 7, "name": "To Honor America", "role": "FOLLOWER", "tag": "FLAG & EAGLE"},
]

def write_float_config(float_id):
    os.makedirs(INCLUDE_DIR, exist_ok=True)
    config_file = os.path.join(INCLUDE_DIR, "float_config.h")
    content = f"""#ifndef FLOAT_CONFIG_H
#define FLOAT_CONFIG_H

// Auto-generated dedicated float identity
#ifndef COMPILED_FLOAT_ID
#define COMPILED_FLOAT_ID {float_id}
#endif

#endif // FLOAT_CONFIG_H
"""
    with open(config_file, "w", encoding="utf-8") as f:
        f.write(content)

def build_binary(float_id=0):
    write_float_config(float_id)
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
    # Generic build first
    build_binary(0)
    for flt in FLOATS:
        build_binary(flt["id"])
    print("==================================================")
    print(" Finished building all 7 float ROM binaries!")
    print("==================================================")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        build_binary(int(sys.argv[1]))
    else:
        build_all()
