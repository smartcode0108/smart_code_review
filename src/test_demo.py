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
    ## Summary
    
    Combines three arguments into a single value.
    
    ## Args:
    
    - `another_long_argument_name`: Description of the first argument.
    - `thrid_argument_for_testing`: Description of the second argument.
    - `some_long_argument_name_that_needs_to_be_split`: Description of the third argument.
    
    ## Returns:
    
    - `type`: The combined value.
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
