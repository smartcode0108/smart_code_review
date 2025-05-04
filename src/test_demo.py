

def multiply_and_add(x, y):
    """
    **Docstring:**
    
    Summary line.
    
    Args:
        param1 (type): description.
    
    Returns:
        type: description.
    """
    return x * y + x


def main():
    """
    Summary line.
    
    Args:
        num (int): The number to be multiplied and added.
    
    Returns:
        int: The result of multiplying the input number by 2 and adding it to itself.
    """
    numbers = [1, 2, 3, 4]
    results = []
    for num in numbers:
        results.append(multiply_and_add(num, 2))
    print("Results:", results)


def test_main():
    """
    Summary line.
    
    Args:
        number (int): description.
        multiplier (int): description.
    
    Returns:
        int: description.
    """
    numbers = [1, 2, 3, 4]
    expected = [1 * 2 + 1, 2 * 2 + 2, 3 * 2 + 3, 4 * 2 + 4]
    for i in range(len(numbers)):
        assert multiply_and_add(numbers[i], 2) == expected[i]


main()
test_main()
