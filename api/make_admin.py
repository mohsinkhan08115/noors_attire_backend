#!/usr/bin/env python3
"""
scripts/make_admin.py
─────────────────────
One-time script to promote an existing user to admin role.

Usage:
  python scripts/make_admin.py --email admin@noorsattire.com

Steps:
  1. Register a normal account via the app or POST /auth/signup
  2. Run this script to grant admin role
  3. Log in to the admin dashboard with those credentials

Requirements:
  - Run from the project ROOT (not from inside scripts/)
  - Your .env file must be present so Firebase initialises correctly
"""

import sys
import os
import argparse

# Allow imports from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load .env before importing anything that needs Firebase
from dotenv import load_dotenv
load_dotenv()

from app.services.firebase_service import get_all, update_one  # noqa: E402 (after sys.path)


def promote_to_admin(email: str) -> None:
    print(f"Looking up user with email: {email}")

    users = get_all("users")
    matches = [u for u in users if u.get("email", "").lower() == email.lower()]

    if not matches:
        print(f"\n❌ No user found with email '{email}'.")
        print("   Register first via POST /auth/signup or through the app, then re-run this script.")
        sys.exit(1)

    user = matches[0]
    current_role = user.get("role", "customer")

    if current_role == "admin":
        print(f"\n✅ User '{user['name']}' is already an admin. Nothing to do.")
        return

    update_one("users", user["id"], {"role": "admin"})
    print(f"\n✅ Success! '{user['name']}' ({email}) has been promoted to admin.")
    print("   They can now log in at your admin dashboard URL.")


def demote_from_admin(email: str) -> None:
    print(f"Looking up user with email: {email}")

    users = get_all("users")
    matches = [u for u in users if u.get("email", "").lower() == email.lower()]

    if not matches:
        print(f"\n❌ No user found with email '{email}'.")
        sys.exit(1)

    user = matches[0]
    update_one("users", user["id"], {"role": "customer"})
    print(f"\n✅ '{user['name']}' ({email}) has been demoted to customer.")


def list_admins() -> None:
    users = get_all("users")
    admins = [u for u in users if u.get("role") == "admin"]

    if not admins:
        print("No admin users found.")
        return

    print(f"\n{'NAME':<25} {'EMAIL':<35} {'ID'}")
    print("─" * 80)
    for a in admins:
        print(f"{a.get('name','?'):<25} {a.get('email','?'):<35} {a.get('id','?')}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage admin users for Noor's Attire")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--promote",  metavar="EMAIL", help="Promote user to admin")
    group.add_argument("--demote",   metavar="EMAIL", help="Demote admin to customer")
    group.add_argument("--list",     action="store_true", help="List all admin users")
    # Shortcut: --email is an alias for --promote (backward compat)
    group.add_argument("--email",    metavar="EMAIL", help="Alias for --promote")

    args = parser.parse_args()

    if args.promote or args.email:
        promote_to_admin(args.promote or args.email)
    elif args.demote:
        demote_from_admin(args.demote)
    elif args.list:
        list_admins()