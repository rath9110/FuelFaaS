"""Fix the admin user role to be uppercase."""
import sqlite3

def fix_admin_role():
    conn = sqlite3.connect('fuelguard.db')
    cursor = conn.cursor()
    
    # Update role to uppercase
    cursor.execute("UPDATE users SET role = 'ADMIN' WHERE username = 'admin'")
    
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    
    if affected > 0:
        print(f"Fixed! Updated {affected} user(s).")
        print("Role is now: ADMIN (uppercase)")
        print("\nYou can now login with:")
        print("  Username: admin")
        print("  Password: admin123")
    else:
        print("No users found to update.")

if __name__ == "__main__":
    fix_admin_role()
