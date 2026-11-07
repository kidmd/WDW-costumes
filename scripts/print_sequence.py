# Print sequence from preset
import json

with open('presets/pete_s_dragon_16x16_printed_81led.json', 'r') as f:
    d = json.load(f)

seq = d.get('sequence', {})
print(json.dumps(seq, indent=2))
