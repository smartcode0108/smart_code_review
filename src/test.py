import sys,os

def add(a,b):return a+b

def  Subtract(a, b ):
  result=a - b
  return result

class calculator:
    def __init__(self,value=0):
        self.value=value

    def multiply(self,x):
        self.value=self.value *x
        return self.value

    def divide(self, x ):
            if x==0:
                print("Cannot divide by zero")