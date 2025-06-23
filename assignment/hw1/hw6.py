s = input()

def is_huiwen(ss:str) -> bool:
    for i in range(ss.__len__()):
        if ss[i] != ss[ss.__len__()-i-1]:
            return False
    return True

for len in reversed(range(s.__len__()+1)):
    to_break = False
    for i in range(s.__len__()+1-len):
        ss = s[i:i+len]
        if is_huiwen(ss):
            print(ss)
            to_break = True
            break
    if to_break:
        break