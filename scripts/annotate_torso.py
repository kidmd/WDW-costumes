import cv2
import numpy as np
from PIL import Image

img = Image.open('assets/Turtle_clean.png').convert('RGBA')
arr = np.array(img)

# Let's crop the torso from y=750 to 1700, x=350 to 1150
torso = arr[750:1700, 350:1150].copy()

# Save clean torso
Image.fromarray(torso).save('scripts/torso_clean.png')

# Let's draw bounding boxes and annotations
annotated = torso.copy()

# Area 1: Left of tie (Viewer's left): y in torso is 850-750=100 to 1250-750=500, x is 450-350=100 to 650-350=300
cv2.rectangle(annotated, (80, 150), (270, 480), (255, 0, 0, 255), 3) # Blue box
cv2.putText(annotated, "Viewer Left (Area 1)", (80, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0, 255), 2)

# Area 2: Right of tie (Viewer's right): y in torso is 850-750=100 to 1670-750=920, x is 650-350=300 to 1050-350=700
cv2.rectangle(annotated, (310, 150), (680, 920), (0, 0, 255, 255), 3) # Red box
cv2.putText(annotated, "Viewer Right / Long Flipper (Area 2)", (310, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255, 255), 2)

Image.fromarray(annotated).save('scripts/torso_annotated.png')
print("Annotated torso saved.")
