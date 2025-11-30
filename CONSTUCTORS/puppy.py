class Puppy:
    def __init__(self, name, breed):
        self.name = name
        self.breed = breed
    
    def bark(self):
        return f"{self.name} says woof!"
    
# Creating a Puppy
my_puppy = Puppy("Buddy", "Labrador")
print(my_puppy.bark())
