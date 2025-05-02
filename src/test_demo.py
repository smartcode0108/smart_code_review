

def add(a, b):
    """
    **Summary:**
    
    Returns the sum of two numbers.
    
    **Args:**
    
        num1 (int): The first number.
        num2 (int): The second number.
    
    **Returns:**
    
        int: The sum of num1 and num2.
    """
    return a + b


def Subtract(a, b):
    """
    **Docstring:**
    
    Summary line.
    
    Args:
        param1 (type): description.
    
    Returns:
        type: description.
    """
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
        """
        Summary line.
        
        Args:
            param1 (type): description.
        
        Returns:
            type: description.
        """
            return None
        return self.value / x

        """
        Summary:
        Returns the value of the `self.value` attribute.
        
        Returns:
        int: The value of `self.value`.
        """

def main():
    """
    Summary line.
        """
        Divides two numbers.
        
        Args:
            self (type): description.
            x (int): divisor.
        
        Returns:
            type: quotient.
        
        Raises:
            ZeroDivisionError: if divisor is zero.
        """
    
    Args:
        param1 (type): description.
    
    Returns:
        type: description.
    """
    calc = calculator()
    print("Add:", add(5, 10))
    print("Subtract:", Subtract(10, 5))
    print("Multiply:", calc.multiply(2))
    print("Divide:", calc.divide(0))


main()
