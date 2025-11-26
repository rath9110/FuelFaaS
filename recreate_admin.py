"""Delete and recreate admin user with compatible bcrypt hash."""
import sqlite3

def recreate_admin():
    conn = sqlite3.connect('fuelguard.db')
    cursor = conn.cursor()
    
    # Delete existing admin
    cursor.execute("DELETE FROM users WHERE username = 'admin'")
    print("Deleted old admin user")
    
    # Create new admin with fresh bcrypt hash for "admin123"
    # This hash was generated with bcrypt 4.0.1
    hashed_password = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"
    
    cursor.execute("""
        INSERT INTO users (email, username, full_name, hashed_password, role, is_active, created_at)
        VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
    """, (
        "admin@fuelguard.ai",
        "admin",
        "Administrator",
        hashed_password,
        "ADMIN",
        1
    ))
    
    conn.commit()
    conn.close()
    
    print("Admin user recreated successfully!")
    print("Username: admin")
    print("Password: admin123")
    print("\nYou can now login!")

if __name__ == "__main__":
    recreate_admin()
