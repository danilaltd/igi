import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myparking.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

# Create admin user
admin = User.objects.create(
    username='admin',
    password=make_password('admin'),
    email='admin@example.com',
    is_superuser=True,
    is_staff=True,
    is_active=True
)
print("Admin user created successfully!") 