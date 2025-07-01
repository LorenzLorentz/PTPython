class Pet:
    def __init__(self, name):
        self.name = name
        self.happiness = 0
        self.smart = 0
        self.health = 0
        
    def play(self):
        self.happiness += 10
        self.smart += 2
        self.health += 6
    
    def eat(self):
        self.happiness += 5
        self.smart += 1
        self.health += 10
        
    def sleep(self):
        self.happiness += 3
        self.smart += 1
        self.health += 5

class Person:
    def __init__(self, name:str, money:int, num_pet:int):
        self.name = name
        self.money = money
        self.num_pet = num_pet

        self.pets = []

    def add(self, pet_name:str):
        self.pets.append(Pet(pet_name))

    def play(self, pet_name:str):
        for pet in self.pets:
            if pet.name == pet_name:
                pet.play()
                self.money -= 10

    def eat(self, pet_name:str):
        for pet in self.pets:
            if pet.name == pet_name:
                pet.eat()
                self.money -= 5

    def sleep(self, pet_name:str):
        for pet in self.pets:
            if pet.name == pet_name:
                pet.sleep()
                self.money -= 3

N = int(input())

pers = []

for _ in range(N):
    name, money, num_pet = input().split()
    money = int(money)
    num_pet = int(num_pet)

    per = Person(name, money, num_pet)

    pets_name = list(map(str, input().split()))
    for pet_name in pets_name:
        per.add(pet_name)

    pers.append(per)

M = int(input())
for _ in range(M):
    per_name, pet_name, op = input().split()

    for per in pers:
        if per.name == per_name:
            if op=="play":
                per.play(pet_name)
            elif op=="eat":
                per.eat(pet_name)
            elif op=="sleep":
                per.sleep(pet_name)

for per in pers:
    print(per.name, end=" ")
    print(per.money, end=" ")

    h_m = -1
    h_s = -1
    h_h = -1

    for pet in per.pets:
        if pet.happiness > h_m:
            h_m = pet.happiness
        if pet.smart > h_s:
            h_s = pet.smart
        if pet.health > h_h:
            h_h = pet.health

    print(h_m, h_s, h_h)