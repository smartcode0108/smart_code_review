

def multiply_and_add(x, y):
    """
    Summary line.
    
    Args:
        param1 (type): description.
    
    Returns:
        type: description.
    """
    return x * y + x


def main():
    """
    ## Multiply and Add Function
    
    Args:
        num (int): The number to multiply and add.
    
    Returns:
        int: The result of multiplying the number by 2 and adding it to the number itself.
    """
    numbers = [1, 2, 3, 4]
    results = []
    for num in numbers:
        results.append(multiply_and_add(num, 2))
    print("Results:", results)


def test_main():
    """
    Summary:
    Calculates the multiplication and addition of each element in a list by a given value.
    
    Args:
        number (int): The element in the list.
        multiplier (int): The value to multiply and add.
    
    Returns:
        int: The result of multiplying and adding the number by the multiplier.
    """
    numbers = [1, 2, 3, 4]
    expected = [1 * 2 + 1, 2 * 2 + 2, 3 * 2 + 3, 4 * 2 + 4]
    for i in range(len(numbers)):
        assert multiply_and_add(numbers[i], 2) == expected[i]


main()
test_main()
