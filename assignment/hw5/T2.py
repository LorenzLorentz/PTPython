import numpy as np
from sklearn.cluster import KMeans

n, d, k = map(int, input().split())
data = np.array([list(map(int, input().split())) for _ in range(n)])

model = KMeans(n_clusters=k, random_state=0, n_init='auto')
model.fit(data)

centers = sorted(model.cluster_centers_.tolist())

for center in centers:
    for x in center:
        print(f"{x:.2f}", end=" ")
    print("")