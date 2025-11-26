"""Test if the password hash works correctly."""
import sqlite3
from passlib.context import CryptContext

# Initialize password hasher
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def test_password():
    # Get the hash from database
    conn = sqlite3.connect('fuelguard.db')
    cursor = conn.cursor()
    cursor.execute("SELECT username, hashed_password FROM users WHERE username = 'admin'")
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        print("ERROR: No admin user found in database!")
        return
    
    username, stored_hash = result
    print(f"Found user: {username}")
    print(f"Stored hash: {stored_hash[:50]}...")
    
    # Test password verification
    test_password = "admin123"
    print(f"\nTesting password: '{test_password}'")
    
    try:
        is_valid = pwd_context.verify(test_password, stored_hash)
        print(f"Password verification result: {is_valid}")
        
        if is_valid:
            print("\nSUCCESS: Password matches!")
        else:
            print("\nFAILED: Password does not match")
            print("Generating new hash...")
            new_hash = pwd_context.hash(test_password)
            print(f"New hash: {new_hash}")
            
    except Exception as e:
        print(f"\nERROR during verification: {e}")

if __name__ == "__main__":
    test_password()
