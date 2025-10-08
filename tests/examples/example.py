def process_data(data_list):
    result = []
    for item in data_list:
        if item > 0:
            result.append(item * 2)
    return result

def calculate_average(nums):
    # Calculate the mean value
    count = len(nums)
    total = 0
    for n in nums:
        total = total + n
    return total / len(nums)

numbers = [1, -2, 3, -4, 5]
processed = process_data(numbers)
print(f"Processed: {processed}")
print(f"Average: {calculate_average(numbers)}")