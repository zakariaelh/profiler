import time

def my_function(n):
    """Performs a computationally intensive task."""
    # Optimized: Using list comprehension and sum() for better performance
    return sum(i * i for i in range(n))

def fibonacci_sum(n):
    # Optimized: Using dynamic programming to calculate Fibonacci numbers
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
    start_time = time.time()
    result = my_function(n)
    end_time = time.time()
    print('Result:', result)
    print('Elapsed time:', end_time - start_time, 'seconds')