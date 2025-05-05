import math


def my_function(x, y):
    """
    Summary line.
    
    Args:
        param1 (type): description.
    
    Returns:
        type: description.
    """
    return x + y


def exampleFunc(a, b):
    """
    **Docstring:**
    
    Summary line.
    
    Args:
        b (type): description.
    
    Returns:
        type: description.
    """
    if a > 5:
        print("Hello")
    else:
        print("Goodbye")
        return b


def calc_area(radius):
    """
    Summary line.
    
    Args:
        param1 (type): description.
    
    Returns:
        type: description.
    """
    result = math.pi * radius * radius
    return result


def some_long_function_name_that_should_be_split_and_should_use_proper_indentation_when_possible(
    """
    Summary line.
    
    Args:
        another_long_argument_name (type): description.
        thrid_argument_for_testing (type): description.
    
    Returns:
        type: description.
    """
    some_long_argument_name_that_needs_to_be_split,
    another_long_argument_name,
    thrid_argument_for_testing,
):
    value = (
        some_long_argument_name_that_needs_to_be_split
        + another_long_argument_name
        + thrid_argument_for_testing
    )
    return value
