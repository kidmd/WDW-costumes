import os

# Check git history or files for turtle
print("Checking repo files for turtle...")
for root, dirs, files in os.walk('.'):
    for f in files:
        if 'turtle' in f.lower():
            print(os.path.join(root, f))
