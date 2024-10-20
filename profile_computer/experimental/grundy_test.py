import time


def my_function(n):
    """Performs a computationally intensive task."""
    result = 0
    for i in range(n):
        result += i * i
    return result


def bar(n):
    result = 0
    for i in range(n):
        for j in range(n):
            result += (i * j) % 2
    return result


def main():
    """Main function to demonstrate profiling."""
    n = 10000000
    result = my_function(n)
    inefficient_result = bar(1000)  # Using a smaller n for bar to avoid extremely long execution times
