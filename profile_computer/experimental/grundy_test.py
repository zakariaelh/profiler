import time
import random

def my_function(n):
    """Performs a computationally intensive task."""
    # Using sum() with a generator expression is faster than a for loop
    # This reduces the number of Python bytecode operations
    return sum(i * i for i in range(n))

def dot_product(a, b):
    """Computes the dot product of two vectors."""
    if len(a) != len(b):
        raise ValueError("Vectors must have the same length")
    
    # Using sum() with zip() is more efficient than nested loops
    # This also avoids the need for temporary variables
    return sum(x * y for x, y in zip(a, b))

def main():
    """Main function to demonstrate profiling."""
    n = 10000000
    result = my_function(n)
    
    # Using list comprehension with map() and random.random is slightly more efficient
    # This avoids the overhead of the range() function
    a = list(map(random.random, [None] * n))
    b = list(map(random.random, [None] * n))