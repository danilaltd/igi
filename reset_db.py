import os
import django
from django.core.management import call_command

def reset_database():
    print("Resetting database...")
    
    # Delete the database file if it exists
    if os.path.exists('db.sqlite3'):
        os.remove('db.sqlite3')
        print("Database file deleted.")
    
    # Run migrations
    print("Running migrations...")
    call_command('makemigrations')
    call_command('migrate')
    
    # Load fixtures using our custom script
    print("Loading fixtures...")
    exec(open('load_fixtures.py').read())
    
    print("Database reset complete!")

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myparking.settings')
    django.setup()
    reset_database() 