source_str = input()
target_str = input()

result = set()

for char in source_str:
    if target_str.find(char) == -1:
        result.add(char)

result = sorted(result)
for char in result:
    print(char, end=" ")