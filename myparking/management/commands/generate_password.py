from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password

class Command(BaseCommand):
    help = 'Generates a password hash for the admin user'

    def handle(self, *args, **options):
        password = 'admin'
        hashed_password = make_password(password)
        self.stdout.write(self.style.SUCCESS(f"Password hash for 'admin': {hashed_password}")) 