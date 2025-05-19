import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myparking.settings')
django.setup()

from django.contrib.auth.models import User

# Delete existing admin user if exists
User.objects.filter(username='admin').delete()

# Create new admin user
admin = User.objects.create_superuser(
    username='admin',
    email='admin@example.com',
    password='admin'
)
print("Admin user recreated successfully!") 