def calculate_average(numbers):
    total = 0
    count = 0
    for num in numbers:
        total = total + num
        count = count + 1

    if count == 0:
        return 0
    average = total / count
    return average

# Test the function
data = [10, 20, 30, 40, 50]
result = calculate_average(data)
print("The average is: " + str(result))