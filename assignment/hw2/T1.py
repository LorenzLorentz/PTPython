*a, = map(int, input().split())

a = sorted(a, reverse=True)

result = 0

while(result<a.__len__() and a[result]>=result):
    result += 1

print(result)