"""Create admin user with a pre-computed bcrypt hash."""
import sqlite3
from datetime import datetime

def create_admin_user():
    # Pre-computed bcrypt hash for "admin123"
    # This is a known valid bcrypt hash
    hashed_password = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU2YqDY5cN8m"
    
    # Connect to database
    conn = sqlite3.connect('fuelguard.db')
    cursor = conn.cursor()
    
    try:
        # Create admin user
        cursor.execute("""
            INSERT INTO users (email, username, full_name, hashed_password, role, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            "admin@fuelguard.ai",
            "admin",
            "Administrator",
            hashed_password,
            "admin",
            1,  # True
            datetime.utcnow().isoformat()
        ))
        
        conn.commit()
        print("Admin user created successfully!")
        print("  Username: admin")
        print("  Password: admin123")
        print("\nYou can now login on the frontend!")
        
    except sqlite3.IntegrityError:
        print("Admin user already exists!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    create_admin_user()
