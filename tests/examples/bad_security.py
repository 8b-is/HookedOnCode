import sqlite3
import os

def get_user(user_id):
    # SQL Injection vulnerability
    conn = sqlite3.connect('users.db')
    query = f"SELECT * FROM users WHERE id = {user_id}"
    result = conn.execute(query).fetchall()
    conn.close()
    return result

def save_password(password):
    # Storing password in plaintext
    with open('passwords.txt', 'a') as f:
        f.write(password + '\n')

def run_command(user_input):
    # Command injection vulnerability
    os.system(f"echo {user_input}")

# Hardcoded API key
API_KEY = "sk-1234567890abcdef"

def divide_numbers(a, b):
    # No zero check
    return a / b