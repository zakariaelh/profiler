import time
from typing import List


def my_function(n: int) -> int:
    """Performs a computationally intensive task."""
    # Using list comprehension for better performance
    return sum(i * i for i in range(n))


def foo(n: int) -> int:
    """Optimized version of the original foo function."""
    # Using a mathematical formula to replace nested loops
    return sum((i * (i - 1) * (2 * i - 1)) // 6 for i in range(1, n + 1))


def main():
    """Main function to demonstrate profiling."""
    n = 10000000
    result = my_function(n)

    rs = foo(5000)
    print(rs)