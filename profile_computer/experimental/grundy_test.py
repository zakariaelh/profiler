import time

def my_function(n):
    """Performs a computationally intensive task."""
    # Use list comprehension and sum() for better performance
    return sum(i * i for i in range(n))

def bar(n):
    # Use numpy for vectorized operations
    import numpy as np
    return np.sum((np.arange(n)[:, None] * np.arange(n)) % 2)


def main():
    """Main function to demonstrate profiling."""
    n = 10000000
    result = my_function(n)
    inefficient_result = bar(1000)  # Using a smaller n for bar to avoid extremely long execution times