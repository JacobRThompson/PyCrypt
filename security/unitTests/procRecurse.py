def factorial(x):
    if x == 1:
        return 1
    else:
        return (x * factorial(x-1))

factorial2 = lambda x: 1 if x == 0 else x * factorial2(x-1)

temp = factorial(7) - factorial2(7)