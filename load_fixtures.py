import os
import django
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myparking.settings')
django.setup()

# List of fixtures in the correct order
fixtures = [
    'users.json',
    'cars.json',
    'parking_spots.json',
    'reviews.json',
    'news.json',
    'vacancies.json',
    'faq.json',
    'company_info.json',
    'service_categories.json',
    'services.json',
    'promocodes.json',
    'coupons.json'
]

# Load each fixture
for fixture in fixtures:
    try:
        print(f"Loading {fixture}...")
        call_command('loaddata', fixture)
        print(f"{fixture} loaded successfully!")
    except Exception as e:
        print(f"Error loading {fixture}: {str(e)}")

print("Fixture loading completed!") 