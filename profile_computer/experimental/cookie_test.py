def some_function(n):
    """Performs a computationally intensive task with a string."""
    result = '.'
    for i in range(n):
        result += result
    return result


def main():
    """Main function to demonstrate profiling with string."""
    n = 14
    result = some_function(n)
    print('Result:', result)
