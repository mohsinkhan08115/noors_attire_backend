import sys
from app.services.firebase_service import update_one, get_one
from app.core.security import hash_password

# ---------------------------------------------------------
# FILL IN YOUR ADMIN CREDENTIALS HERE
# ---------------------------------------------------------
USER_ID = "-OpOldjUFjDyeWJI-JlI"
ADMIN_EMAIL = "noorattire247@gmail.com"
NEW_PASSWORD = "noorattire247"
# ---------------------------------------------------------

def reset_admin():
    print(f"Checking if user '{USER_ID}' exists...")
    user = get_one("users", USER_ID)
    
    if not user:
        print(f"\nERROR: User with ID '{USER_ID}' does not exist in the database.")
        sys.exit(1)

    print("User found. Generating secure password hash...")
    new_hash = hash_password(NEW_PASSWORD)

    print("Updating admin credentials in Firebase...")
    update_data = {
        "email": ADMIN_EMAIL,
        "password_hash": new_hash,
        "role": "admin"
    }

    updated_user = update_one("users", USER_ID, update_data)
    
    if updated_user:
        print("\n✅ Admin credentials updated successfully!")
        print(f"Email: {updated_user.get('email')}")
        print(f"Role: {updated_user.get('role')}")
        print("Password was hashed successfully and saved securely.")
    else:
        print("\n❌ ERROR: Failed to update the admin user.")
        sys.exit(1)

if __name__ == "__main__":
    if ADMIN_EMAIL == "noorattire247@gmail.com" or NEW_PASSWORD == "noorattire247":
        print("Please edit 'reset_admin.py' and replace the placeholders with your actual email and password.")
        sys.exit(1)
        
    reset_admin()
