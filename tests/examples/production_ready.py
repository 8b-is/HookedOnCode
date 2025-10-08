#!/usr/bin/env python3
"""
Production-ready service with proper error handling
"""

import hashlib
import json
import sqlite3
from typing import Dict, Optional

def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def get_user_by_id(user_id: int, db_path: str) -> Optional[Dict]:
    """Safely fetch user from database"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        return dict(result) if result else None
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None

def divide_safely(a: float, b: float) -> Optional[float]:
    """Division with zero check"""
    if b == 0:
        return None
    return a / b

def load_config(config_path: str) -> Dict:
    """Load JSON configuration file"""
    with open(config_path, 'r') as f:
        return json.load(f)

if __name__ == "__main__":
    print("Service ready")