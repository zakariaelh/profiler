import time


def my_function(n):
    """Performs a computationally intensive task."""
    result = 0
    for i in range(n):
        result += i * i
    return result


def main():
    """Main function to demonstrate profiling."""
    n = 10000000
    result = my_function(n)
