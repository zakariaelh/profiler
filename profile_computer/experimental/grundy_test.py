import time


def my_function(n):
    """Performs a computationally intensive task."""
    result = 0
    for i in range(n):
        result += i * i
    return result


def zee(n):
    result = []
    for i in range(n):
        temp = []
        for j in range(i):
            temp.append(j)
        result.append(sum(temp))
    return sum(result)


def main():
    """Main function to demonstrate profiling."""
    n = 10000000
    result = my_function(n)
    res = zee(n // 1000)  # Using a smaller n to avoid excessive runtime
