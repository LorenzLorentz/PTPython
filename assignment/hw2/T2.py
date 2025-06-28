import re

address = input()

matchobj = re.match(r"(\w+)@([a-zA-Z]+(\.[a-zA-Z]+)+)", address)

print("True" if matchobj else "False")