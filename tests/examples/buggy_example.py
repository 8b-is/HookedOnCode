import requests

def fetch_user_data(user_id):
    # No error handling
    response = requests.get(f"https://api.example.com/users/{user_id}")
    data = response.json()

    # Potential division by zero
    average = sum(data['scores']) / len(data['scores'])

    # SQL injection vulnerability
    query = f"SELECT * FROM users WHERE id = {user_id}"

    # Hardcoded credentials
    password = "admin123"

    return data

# Global mutable default
def add_to_list(item, list=[]):
    list.append(item)
    return list