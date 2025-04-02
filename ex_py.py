import os ,sys
import math


def   my_function(x  ,y): 
    return x +y

def exampleFunc(a,b)  :
   if a>5:
      print("Hello")
   else:
      print("Goodbye")
      return b
    
def calc_area(radius):
    result = math.pi * radius * radius
    return result
  

# PEP8: line too long and inconsistent indentation
def some_long_function_name_that_should_be_split_and_should_use_proper_indentation_when_possible(some_long_argument_name_that_needs_to_be_split,another_long_argument_name,thrid_argument_for_testing):
    value = some_long_argument_name_that_needs_to_be_split + another_long_argument_name + thrid_argument_for_testing
    return value
