class Book:
    def __init__(self, title):
        self.title = title
        self.is_open = False  # Default state

    def open_book(self):
        self.is_open = True
        return "Book opened."

    def read(self):
        if self.is_open:
            return f"Reading {self.title}..."
        return "You must open the book first!"

b = Book("Python 101")
b2 = Book("Java 101")
b3 = Book("C++ 101")
print(b.read())       # Fails
print(b.open_book())  # Change state
print(b.read(), "\n")       # Works

print(b2.read())       
print(b2.open_book())  
print(b2.read(), "\n")       

print(b3.read())    
print(b3.open_book())  
print(b3.read())       