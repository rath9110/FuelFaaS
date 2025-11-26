"""Check what users exist in the database."""
import asyncio
import sqlite3

def check_users():
    conn = sqlite3.connect('fuelguard.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT username, email, role, is_active FROM users")
        users = cursor.fetchall()
        
        if users:
            print(f"Found {len(users)} users:")
            for user in users:
                print(f"  - Username: {user[0]}, Email: {user[1]}, Role: {user[2]}, Active: {user[3]}")
        else:
            print("No users found in database!")
            
    except sqlite3.OperationalError as e:
        print(f"Error: {e}")
        print("Users table might not exist yet.")
    finally:
        conn.close()

if __name__ == "__main__":
    check_users()
