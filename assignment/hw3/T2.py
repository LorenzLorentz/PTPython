import numpy as np

a = list(map(int, input().split()))
b = list(map(int, input().split()))

a = np.array(a)
b = np.array(b)

sim = np.dot(a, b)/(np.sqrt(np.dot(a,a) * np.dot(b,b)))
print(f"{sim:.2f}")