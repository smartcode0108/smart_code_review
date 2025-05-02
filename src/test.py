

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
    Summary:
    Multiplies each number in a list by 2 and appends the result to a new list.
    
    Args:
        numbers (list): A list of numbers.
    
    Returns:
        list: A new list containing the results of multiplying each number in the input list by 2.
    """
    numbers = [1, 2, 3, 4]
    results = []
    for num in numbers:
        results.append(multiply_and_add(num, 2))
    print("Results:", results)


def test_main():
    """
    Summary:
    Calculates the expected result for a given list of numbers using the formula `x * 2 + x`.
    
    Args:
        numbers (list): A list of numbers.
    
    Returns:
        list: A list of expected results.
    """
    numbers = [1, 2, 3, 4]
    expected = [1 * 2 + 1, 2 * 2 + 2, 3 * 2 + 3, 4 * 2 + 4]
    for i in range(len(numbers)):
        assert multiply_and_add(numbers[i], 2) == expected[i]


main()
test_main()
