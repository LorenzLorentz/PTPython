n, m = map(int, input().split())

dic = {}

for _ in range(n):
    key, value = map(str, input().split())
    dic[key] = value if key in dic.keys() else dic.setdefault(key, value)

for _ in range(m):
    vec = input().split()
    if vec.__len__() == 2:
        op, key = vec
        if op=="Q":
            print(dic[key] if key in dic.keys() else "None")
        elif op=="D":
            if key in dic.keys():
                dic.pop(key)
    elif vec.__len__() == 3:
        op, key, value = vec
        if op=="A":
            dic[key] = value if key in dic.keys() else dic.setdefault(key, value)

sort = sorted(dic)
for key in sort:
    print(key, end=" ")
    print(dic[key])