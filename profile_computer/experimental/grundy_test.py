import time

def my_function(n):
    """Performs a computationally intensive task."""
    # Use list comprehension and sum for better performance
    return sum(i * i for i in range(n))

def fibonacci_sum(n):
    # Use dynamic programming to optimize Fibonacci calculation
    if n <= 1:
        return n
    fib = [0] * (n + 1)
    fib[1] = 1
    total_sum = 1
    for i in range(2, n + 1):
        fib[i] = fib[i-1] + fib[i-2]
        total_sum += fib[i]
    return total_sum

def main():
    """Main function to demonstrate profiling."""
    n = 10000000
    fib_sum = fibonacci_sum(20)
    result = my_function(n)
    # Add print statements to prevent optimization
    print(f"Fibonacci sum: {fib_sum}")
    print(f"My function result: {result}")