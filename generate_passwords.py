import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myparking.settings')
django.setup()

from django.contrib.auth.hashers import make_password

# Генерируем хэш для пароля admin
admin_hash = make_password('admin')
print(f"Admin password hash: {admin_hash}")

# Генерируем хэш для пароля staff
staff_hash = make_password('staff')
print(f"Staff password hash: {staff_hash}")

# Генерируем хэш для пароля user
user_hash = make_password('user')
print(f"User password hash: {user_hash}") 