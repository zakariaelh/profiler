import time


def my_function(n):
    """Performs a computationally intensive task."""
    result = 0
    for i in range(n):
        result += i * i
    return result

def fibonacci_sum(n):
    def fib(x):
        if x <= 1:
            return x
        return fib(x - 1) + fib(x - 2)

    total_sum = 0
    for i in range(n + 1):
        total_sum += fib(i)

    return total_sum

def main():
    """Main function to demonstrate profiling."""
    n = 10000000
    fib_sum = fibonacci_sum(20)
    result = my_function(n)
