import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myparking.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

# Create users with proper password hashes
users = [
    {
        "model": "auth.user",
        "pk": 1,
        "fields": {
            "password": make_password('admin'),
            "last_login": None,
            "is_superuser": True,
            "username": "admin",
            "first_name": "Admin",
            "last_name": "User",
            "email": "admin@example.com",
            "is_staff": True,
            "is_active": True,
            "date_joined": "2024-01-01T00:00:00Z"
        }
    }
]

# Add client users
for i in range(1, 11):
    users.append({
        "model": "auth.user",
        "pk": i + 1,
        "fields": {
            "password": make_password('user'),
            "last_login": None,
            "is_superuser": False,
            "username": f"user{i}",
            "first_name": "Client",
            "last_name": f"{i}",
            "email": f"user{i}@example.com",
            "is_staff": False,
            "is_active": True,
            "date_joined": "2024-01-01T00:00:00Z"
        }
    })

# Add staff users
for i in range(1, 11):
    users.append({
        "model": "auth.user",
        "pk": i + 11,
        "fields": {
            "password": make_password('staff'),
            "last_login": None,
            "is_superuser": False,
            "username": f"staff{i}",
            "first_name": "Staff",
            "last_name": f"{i}",
            "email": f"staff{i}@example.com",
            "is_staff": True,
            "is_active": True,
            "date_joined": "2024-01-01T00:00:00Z"
        }
    })

# Save to fixtures file
with open('myparking/fixtures/users.json', 'w', encoding='utf-8') as f:
    json.dump(users, f, indent=4, ensure_ascii=False)

print("Fixtures updated successfully!") 