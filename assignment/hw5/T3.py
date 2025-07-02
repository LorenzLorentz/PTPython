import sys
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity

m1, m2, n, a, b = map(int, input().split())

dataA, rowA, colA = [], [], []
for _ in range(a):
    i, j, k = map(int, input().split())
    rowA.append(i - 1)
    colA.append(j - 1)
    dataA.append(k)

dataB, rowB, colB = [], [], []
for _ in range(b):
    i, j, k = map(int, input().split())
    rowB.append(i - 1)
    colB.append(j - 1)
    dataB.append(k)

A = csr_matrix((dataA, (rowA, colA)), shape=(m1, n))
B = csr_matrix((dataB, (rowB, colB)), shape=(m2, n))

max = 0
arg1 = 0
arg2 = 0

block = 512
for start in range(0, m1, block):
    sim = cosine_similarity(A[start:min(start+block, m1)], B)
    index = np.argmax(sim)
    max_ = sim.flat[index]
    
    if max_ > max:
        max = max_
        arg1 = start + (index//m2)
        arg2 = index % m2

print(arg1+1, arg2+1)