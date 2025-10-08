def process_user_data(users):
    results = {}
    for user in users:
        # No null checking
        name = user["name"]
        age = user["age"]

        # Magic number
        if age > 65:
            discount = 0.15
        else:
            discount = 0

        # Inefficient string concatenation in loop
        message = "User: " + name
        message = message + " Age: " + str(age)
        message = message + " Discount: " + str(discount * 100) + "%"

        results[name] = message

    # No return value check
    return results

# Testing with empty list - will return empty dict
data = process_user_data([])