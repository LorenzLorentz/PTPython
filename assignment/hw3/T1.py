import numpy as np

def op(arr:np.ndarray) -> np.ndarray:
    arr[[0, -1], :] = arr[[-1, 0], :]
    arr[:, [0, -1]] = arr[:, [-1, 0]]
    arr = 1-arr
    return arr

T = int(input())

for _ in range(T):
    n, m = map(int, input().split())
    a = []
    for __ in range(n):
        *b, = map(int, input().split())
        a.append(b)
    
    a = np.array(a)
    a = op(a)

    """
    for i in range(a.shape[0]):
        for j in range(a.shape[1]):
            print(a[i,j], end=" ")
        print("")
    """

    for row in a:
        print(*row)