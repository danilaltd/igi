import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myparking.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

# Update admin user password
admin = User.objects.get(username='admin')
admin.password = make_password('admin')
admin.save()
print("Admin password updated successfully!") 