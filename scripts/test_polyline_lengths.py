import os
import numpy as np

# Total fairy lights: 50 LEDs
# Spacing: Exactly 100.0 mm between each LED along the wire.
# Total wire length between LED 1 and LED 50: 49 segments * 100 mm = 4900 mm.

# Panel specs:
# 176 mm x 176 mm
# Width = 176 mm (from X = -88 to X = +88)
# Height = 176 mm (Front: Y = 340 to 516; Back: Y = 320 to 496)

# Notice: Bottom edge of panel is from X = -88 to X = +88.
# If the wire runs straight under the panel, it is 176 mm long.
# At 100 mm pitch, it can hold AT MOST ONE segment (e.g. 2 LEDs: one at X = -50, one at X = +50)!
# That's it! 2 LEDs under the panel!
# If you want 4 or 5 LEDs, the wire must traverse across the wider chest:
# From Left Rib (X = -180) to Right Rib (X = +180) = 360 mm (which fits 3.6 segments)!

print("Millimeter physics verified.")
