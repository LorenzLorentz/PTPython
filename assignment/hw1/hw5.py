N = int(input())

cnt = {}
for _ in range(N):
    a = int(input())
    if a in cnt.keys():
        cnt[a] += 1
    else:
        cnt[a] = 1
argmax = 0
max = 0
for key, res in cnt.items():
    if res > max:
        argmax = key
        max = res
print(argmax)