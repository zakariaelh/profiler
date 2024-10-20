import time

def my_function(n):
    """Performs a computationally intensive task."""
    # Optimization: Use the formula for sum of squares instead of a loop
    # This reduces time complexity from O(n) to O(1)
    return (n * (n + 1) * (2 * n + 1)) // 6

def zee(n):
    # Optimization: Use list comprehension and avoid unnecessary temp lists
    # This reduces memory usage and improves performance
    result = [sum(range(i)) for i in range(n)]
    return sum(result)

def main():
    """Main function to demonstrate profiling."""
    n = 10000000
    result = my_function(n)
    res = zee(n // 1000)  # Using a smaller n to avoid excessive runtime
    # Optimization: Return results to avoid unused variables
    return result, res