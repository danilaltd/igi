from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
import os

class Command(BaseCommand):
    help = 'Resets the database to initial state'

    def handle(self, *args, **options):
        self.stdout.write('Resetting database...')
        
        # Удаляем файл базы данных
        db_path = 'db.sqlite3'
        if os.path.exists(db_path):
            os.remove(db_path)
            self.stdout.write('Database file removed')
        
        # Применяем миграции заново
        call_command('migrate')
        self.stdout.write('Migrations applied')
        
        # Загружаем начальные данные
        call_command('loaddata', 'initial_data')
        self.stdout.write('Initial data loaded')
        
        self.stdout.write(self.style.SUCCESS('Database has been reset successfully!')) 