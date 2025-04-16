import os
import sys  

def greet(name):
    print("Hello, " + name)

def unused_function():
    x = 5
    y = 6
    return x + y

class Person:
    def __init__(self, name, age):
         self.name = name
         self.age = age
    def get_details(self):
        return f"{self.name} is {self.age} years old."

greet("Alice")
