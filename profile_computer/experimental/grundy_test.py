import time
import random


def my_function(n):
    """Performs a computationally intensive task."""
    result = 0
    for i in range(n):
        result += i * i
    return result

def dot_product(a, b):
    """Computes the dot product of two vectors."""
    if len(a) != len(b):
        raise ValueError("Vectors must have the same length")
    
    result = 0
    for i in range(len(a)):
        temp = a[i]
        for _ in range(b[i]):
            result += temp
    
    return result


def main():
    """Main function to demonstrate profiling."""
    n = 10000000
    result = my_function(n)

    n = 100000
    a = [random.random() for i in range(n)]
    b = [random.random() for i in range(n)]

    res = dot_product(a, b)
    
