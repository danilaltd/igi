import os
import django
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myparking.settings')
django.setup()

from django.core.management import call_command
from django.db import connection
from django.contrib.auth.models import User

def check_fixture_exists(fixture_path):
    return Path(fixture_path).exists()

def load_fixtures():
    print("Loading fixtures...")
    fixtures = [
        # Users (includes all user data)
        'myparking/fixtures/users.json',
        
        # Базовые данные
        'myparking/fixtures/settings.json',
        
        # Основной контент
        'myparking/fixtures/news.json',
        'myparking/fixtures/vacancies.json',
        'myparking/fixtures/reviews.json',
        'myparking/fixtures/faq.json',
        'myparking/fixtures/company_info.json',
        
        # Парковки и автомобили
        'myparking/fixtures/parking_spots.json',
        'myparking/fixtures/cars.json',
        
        # Услуги
        'myparking/fixtures/service_categories.json',
        'myparking/fixtures/services.json',
        
        # Платежи и промо
        'myparking/fixtures/promocodes.json',
        'myparking/fixtures/coupons.json'
    ]
    
    success = True
    for fixture in fixtures:
        try:
            if not check_fixture_exists(fixture):
                print(f"Warning: Fixture {fixture} not found, skipping...")
                continue
                
            print(f"Loading {fixture}...")
            call_command('loaddata', fixture, verbosity=0)
            print(f"{fixture} loaded successfully!")
        except Exception as e:
            print(f"Error loading {fixture}: {str(e)}")
            success = False
    
    if success:
        print("All fixtures loaded successfully!")
    else:
        print("Some fixtures failed to load. Check the errors above.")
    
    return success

if __name__ == '__main__':
    load_fixtures() 