import time


def some_function(n):
    """Performs a computationally intensive task with a string."""
    # Use string multiplication instead of repeated concatenation
    # This is more efficient for large strings
    return '.' * (2**n - 1)  # 2^n - 1 gives the same result as the original function

def main():
    """Main function to demonstrate profiling with string."""
    n = 15
    start_time = time.time()
    result = some_function(n)
    end_time = time.time()
    # Use f-strings for more efficient string formatting
    print(f'Result: {result}')
    print(f'Elapsed time: {end_time - start_time} seconds')