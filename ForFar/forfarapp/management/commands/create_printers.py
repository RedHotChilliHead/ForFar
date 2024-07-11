from django.core.management.base import BaseCommand

from forfarapp.models import Printer


class Command(BaseCommand):
    """
    Создание принтеров
    """
    def handle(self, *args, **options):
        self.stdout.write("Create new printers")  # для проверки создания
        count_key = 1
        for p in range(1, 6):
            printer, created = Printer.objects.get_or_create(name=f"Kitchen Printer {p}",
                                                             api_key=f"generated_api_key_{count_key}",
                                                             check_type="kitchen",
                                                             point_id=p)
            count_key += 1
            printer, created = Printer.objects.get_or_create(name=f"Client Printer {p}",
                                                             api_key=f"generated_api_key_{count_key}",
                                                             check_type="client",
                                                             point_id=p)
            count_key += 1