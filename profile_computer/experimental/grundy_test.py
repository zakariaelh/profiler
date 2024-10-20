import time


def my_function(n):
    """Performs a computationally intensive task."""
    # Use the formula for sum of squares: n * (n + 1) * (2n + 1) / 6
    # This reduces time complexity from O(n) to O(1)
    return (n * (n + 1) * (2 * n + 1)) // 6


def main():
    """Main function to demonstrate profiling."""
    n = 10000000
    start_time = time.time()
    result = my_function(n)
    end_time = time.time()
    print('Result:', result)
    print('Elapsed time:', end_time - start_time, 'seconds')
    # Add timing for the function call only
    function_time = end_time - start_time
    print('Function execution time:', function_time, 'seconds')