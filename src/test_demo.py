def add(a, b):
    """
    Summary line.
    
    Args:
        param1 (type): description.
    
    Returns:
        type: description.
    """
    return a + b


def Subtract(a, b):
    """
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
            return None
        return self.value / x
        """
        Summary line.
        
        Args:
            param1 (type): description.
        
        Returns:
            type: description.
        """


def main():
        """
        Summary:
        Returns the value of the current object.
        
        Returns:
        int: The value of the object.
        """
    """
    **Docstring:**
    
    Summary line.
        """
        Summary:
        Divides self.value by x and returns the result. Prints an error message if x is zero.
        
        Args:
            x (int): The divisor.
        
        Returns:
            float: The result of the division.
        
        Side Effects:
        Prints an error message if x is zero.
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
