import os
import pickle

def load_user_data(filename):
    # Insecure deserialization
    with open(filename, 'rb') as f:
        return pickle.load(f)

def execute_command(user_input):
    # Command injection vulnerability
    result = os.system(f"echo Processing: {user_input}")
    return result

def divide(a, b):
    # No zero check
    return a / b

# SQL injection prone
def get_user(db, user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return db.execute(query)

# Infinite recursion
def countdown(n):
    print(n)
    countdown(n - 1)