import time


def my_function(n):
    """Performs a computationally intensive task."""
    return sum(i * i for i in range(n))


def main():
    """Main function to demonstrate profiling."""
    n = 10000000  # Reverting to original value
    start_time = time.time()
    result = my_function(n)
    end_time = time.time()
    print('Result:', result)
    print('Elapsed time:', end_time - start_time, 'seconds')