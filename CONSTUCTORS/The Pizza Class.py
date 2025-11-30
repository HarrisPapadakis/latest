class Pizza:
    def __init__(self, size, toppings):
        self.size = size
        self.toppings = toppings # Available list

    def cook(self):
        return f"Cooking {self.size} pizza with {self.toppings}"
    
p = Pizza("Large",["Cheese", "Pepperoni"])
print(p.cook())
