import time

def my_function(n):
    """Performs a computationally intensive task."""
    # Optimization: Use list comprehension and sum() for better performance
    # This eliminates the need for an explicit loop and reduces function call overhead
    return sum(i * i for i in range(n))

def fibonacci_sum(n):
    # Optimization: Use dynamic programming to calculate Fibonacci numbers
    # This reduces time complexity from O(2^n) to O(n)
    if n <= 1:
        return n
    fib = [0] * (n + 1)
    fib[1] = 1
    for i in range(2, n + 1):
        fib[i] = fib[i-1] + fib[i-2]
    return sum(fib)

def main():
    """Main function to demonstrate profiling."""
    n = 10000000
    result = my_function(n)
    res = fibonacci_sum(20)
    # Optimization: Add print statements to prevent dead code elimination
    print(f"Result of my_function: {result}")
    print(f"Result of fibonacci_sum: {res}")