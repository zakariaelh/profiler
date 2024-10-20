import time


def some_function(n):
    """Performs a computationally intensive task with a string."""
    result = '.'
    for i in range(n):
        result += result
    return result


def main():
    """Main function to demonstrate profiling with string."""
    n = 15
    start_time = time.time()
    result = some_function(n)
    end_time = time.time()
    print('Result:', result)
    print('Elapsed time:', end_time - start_time, 'seconds')
