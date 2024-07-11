import os
from celery import Celery
from django.conf import settings

# Установка переменной окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ForFar.settings')

# Создание объекта Celery
celery = Celery('ForFar', broker=settings.CELERY_BROKER_URL)

# Загрузка конфигурации из настроек Django
celery.config_from_object('django.conf:settings', namespace='CELERY')

# Автообнаружение задач в приложениях Django
celery.autodiscover_tasks()

# if __name__ == '__main__':
#     celery.start()