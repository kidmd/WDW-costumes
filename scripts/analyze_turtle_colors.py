import numpy as np
from PIL import Image
from sklearn.cluster import KMeans

img = Image.open('assets/Turtle_clean.png').convert('RGBA')
arr = np.array(img)
alpha = arr[:, :, 3]
fg = arr[alpha > 128][:, :3]

# Run KMeans with 5 clusters to see what the natural 5 colors are
kmeans = KMeans(n_clusters=5, random_state=42, n_init=10).fit(fg)
centers = np.round(kmeans.cluster_centers_).astype(int)

counts = np.bincount(kmeans.labels_)
for i in range(5):
    hex_code = '#{:02x}{:02x}{:02x}'.format(centers[i][0], centers[i][1], centers[i][2])
    print(f"Cluster {i}: RGB={centers[i]} Hex={hex_code} Count={counts[i]} ({counts[i]/len(fg)*100:.1f}%)")

# Also check unique colors or top 20 colors
unique_colors, color_counts = np.unique(fg, axis=0, return_counts=True)
sort_idx = np.argsort(-color_counts)
print("\nTop 15 exact colors:")
for i in range(min(15, len(sort_idx))):
    idx = sort_idx[i]
    c = unique_colors[idx]
    hex_code = '#{:02x}{:02x}{:02x}'.format(c[0], c[1], c[2])
    print(f"RGB={c} Hex={hex_code} Count={color_counts[idx]} ({color_counts[idx]/len(fg)*100:.2f}%)")
