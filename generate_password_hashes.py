import os
import django
from django.contrib.auth.hashers import make_password

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myparking.settings')
django.setup()

# Список пользователей и их паролей
users = [
    {"username": "admin", "password": "admin123"},
    {"username": "client1", "password": "client123"},
    {"username": "employee1", "password": "employee123"},
    {"username": "security1", "password": "security123"},
    {"username": "client2", "password": "client123"}
]

# Генерируем хеши
for user in users:
    hashed_password = make_password(user["password"])
    print(f'Username: {user["username"]}')
    print(f'Password: {user["password"]}')
    print(f'Hash: {hashed_password}')
    print('---') 