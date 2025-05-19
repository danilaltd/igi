import os
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Clears all log files'

    def handle(self, *args, **options):
        logs_dir = os.path.join(settings.BASE_DIR, 'logs')
        if os.path.exists(logs_dir):
            cleared = 0
            for log_file in os.listdir(logs_dir):
                if log_file.endswith('.log'):
                    log_path = os.path.join(logs_dir, log_file)
                    try:
                        with open(log_path, 'w') as f:
                            f.write('')
                        cleared += 1
                        self.stdout.write(self.style.SUCCESS(f'Cleared: {log_file}'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error clearing {log_file}: {str(e)}'))
            
            self.stdout.write(self.style.SUCCESS(f'Successfully cleared {cleared} log files'))
        else:
            self.stdout.write(self.style.WARNING('Logs directory not found')) 