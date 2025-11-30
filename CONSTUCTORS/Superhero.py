class Superhero:
    def __init__(self, name, power): #Αρχικοποίηση 
        self.name = name  # Όνομα υπερήρωα
        self.power = power # Δύμανη υπερήρωα
    def attack(self):  # Μέθοδος επίθεσης 
        return f"{self.name} uses {self.power}!" # Επιστροφή μηνύματος

hero1 = Superhero("Thor", "Hammer Smash")
hero2 = Superhero("Iron Man", "Repulsor rays")
hero3 = Superhero("Spider Man", "Web swing")
hero4 = Superhero("Captain America", "Shield")
   
print(hero1.attack())
print(hero2.attack())
print(hero3.attack())
print(hero4.attack())