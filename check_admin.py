import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myparking.settings')
django.setup()

from django.contrib.auth.models import User

# Check admin user
admin = User.objects.get(username='admin')
print(f"Username: {admin.username}")
print(f"Email: {admin.email}")
print(f"Is superuser: {admin.is_superuser}")
print(f"Is staff: {admin.is_staff}")
print(f"Is active: {admin.is_active}")
print(f"Password hash: {admin.password}") 