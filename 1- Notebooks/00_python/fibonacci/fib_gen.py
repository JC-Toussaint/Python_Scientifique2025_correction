#fib_gen.py
""" fibonacci series """

def fib_gen(n):   # return Fibonacci series up to n
    result = []
    a, b = 0, 1
    while b < n:
        result.append(b)
        a, b = b, a+b
    return result

# test de la fonction fib
if __name__ == "__main__":
    print(fib_gen(10))
