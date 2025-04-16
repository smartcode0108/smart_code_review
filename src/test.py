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
import sys
import os


def add(a: int, b: int) -> int:
    """Adds two numbers together.

    Args:
        a (int): The first number to be added.
        b (int): The second number to be added.

    Returns:
        int: The sum of the two numbers.
    """
    return a + b


def subtract(a: int, b: int) -> int:
    """Subtracts one number from another.

    Args:
        a (int): The number to be subtracted from.
        b (int): The number to be subtracted.

    Returns:
        int: The difference between the two numbers.
    """
    return a - b


class Calculator:
    def __init__(self, value=0) -> None:
        """Initializes the calculator with an initial value.

        Args:
            value (int): The initial value of the calculator. Defaults to 0.
        """
        self.value = value

    def multiply(self, x: int) -> int:
        """Multiplies the current value by a given number.

        Args:
            x (int): The number to be multiplied by.

        Returns:
            int: The product of the two numbers.
        """
        self.value = self.value * x
        return self.value

    def divide(self, x: int) -> Union[int, None]:
        """Divides the current value by a given number.

        Args:
            x (int): The number to be divided by.

        Returns:
            int: The quotient of the two numbers, or None if the second argument is 0.
        """
        if x == 0:
            print("Cannot divide by zero")
            return None
        self.value = self.value / x
        return self.value


def main():
    calc = Calculator()
    print("Add:", add(5, 10))
    print("Subtract:", subtract(10, 5))
    print("Multiply:", calc.multiply(2))
    print("Divide:", calc.divide(3))


main()