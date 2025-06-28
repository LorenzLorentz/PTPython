import math

a, b, c = map(float, input().split())

if a==0:
    if b==0:
        if c==0:
            print(5)
        else:
            print(4)
    else:
        print(6)
        print(f"{-c/b:.2f}")
else:
    if b**2-4*a*c<0:
        print(3)
    elif b**2-4*a*c>0:
        print(1)
        if a>0:
            print(f"{(-b-math.sqrt(b**2-4*a*c))/(2*a):.2f}" +" "+f"{(-b+math.sqrt(b**2-4*a*c))/(2*a):.2f}")
        else:
            print(f"{(-b+math.sqrt(b**2-4*a*c))/(2*a):.2f}" +" "+f"{(-b-math.sqrt(b**2-4*a*c))/(2*a):.2f}")
    else:
        print(2)
        print(f"{-b/(2*a):.2f}")