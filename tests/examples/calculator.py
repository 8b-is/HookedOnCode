def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    result = 0
    for i in range(b):
        result = result + a
    return result

def divide(a, b):
    return a / b

# Test
print(multiply(5, 3))
print(divide(10, 2))
