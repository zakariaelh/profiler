def fibonacci_sum(n):
    def fib(x):
        if x <= 1:
            return x
        return fib(x - 1) + fib(x - 2)

    total_sum = 0
    for i in range(n + 1):
        total_sum += fib(i)

    return total_sum

def main():
    n = 1000
    fibonacci_sum(n)