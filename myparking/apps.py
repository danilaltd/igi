from django.apps import AppConfig
import os
import logging


class MyparkingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myparking'

    def ready(self):
        # Очистка логов при запуске
        logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        if os.path.exists(logs_dir):
            for log_file in os.listdir(logs_dir):
                if log_file.endswith('.log'):
                    log_path = os.path.join(logs_dir, log_file)
                    try:
                        with open(log_path, 'w') as f:
                            f.write('')  # Очищаем файл
                        logging.info(f"Cleared log file: {log_file}")
                    except Exception as e:
                        logging.error(f"Error clearing log file {log_file}: {str(e)}")
