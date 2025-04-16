import sys
import os


def add(a, b):
    return a + b


def Subtract(a, b):
    result = a - b
    return result


class calculator:
    def __init__(self, value=0):
        self.value = value

    def multiply(self, x):
        self.value = self.value * x
        return self.value

    def divide(self, x):
        if x == 0:
            print("Cannot divide by zero")
            return None
        return self.value / x


def main():
    calc = calculator()
    print("Add:", add(5, 10))
    print("Subtract:", Subtract(10, 5))
    print("Multiply:", calc.multiply(2))
    print("Divide:", calc.divide(0))


main()
