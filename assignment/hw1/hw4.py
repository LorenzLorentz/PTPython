n = int(input())
*a, = map(int, input().split())
target = int(input())

for i in range(n):
    to_break = False
    for j in range(i+1, n):
        if(a[i]+a[j]==target):
            print(i, j)
            to_break = False
    if to_break:
        break