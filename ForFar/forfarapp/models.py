from django.db import models


class Printer(models.Model):
    """
    Модель принтера
    Каждый принтер печатает только свой тип чеков. Поле api_key принимает уникальные значения, по нему однозначно определяется принтер.
    Для этой модели должны быть fixtures (принтеры для обоих типов чеков для нескольких точек).
    """
    KITCHEN = 'kitchen'
    CLIENT = 'client'

    CHECK_TYPE_CHOICES = [
        (KITCHEN, 'Kitchen'),
        (CLIENT, 'Client'),
    ]

    name = models.CharField(blank=False, null=False, max_length=100)  # название принтера
    api_key = models.CharField(blank=False, null=False, max_length=300, unique=True)  # ключ доступа к API
    check_type = models.CharField(max_length=10, choices=CHECK_TYPE_CHOICES, blank=False)  # тип чека которые печатает принтер kitchen|client
    point_id = models.IntegerField(blank=True, null=True)  # точка к которой привязан принтер

    def __str__(self):
        return self.name

class Check(models.Model):
    """
    Модель чека
    Информация о заказе для каждого чека хранится в JSON
    """
    KITCHEN = 'kitchen'
    CLIENT = 'client'

    NEW = 'new'
    RENDERED = 'rendered'
    PRINTED = 'printed'

    CHECK_TYPE_CHOICES = [
        (KITCHEN, 'Kitchen'),
        (CLIENT, 'Client'),
    ]

    CHECK_STATUS_CHOICES = [
        (NEW, 'new'),
        (RENDERED, 'rendered'),
        (PRINTED, 'printed'),
    ]

    printer = models.ForeignKey(Printer, on_delete=models.DO_NOTHING)  # принтер
    type = models.CharField(max_length=10, choices=CHECK_TYPE_CHOICES, blank=False)  # тип чека
    order = models.JSONField()  # информация о заказе
    status = models.CharField(max_length=10, choices=CHECK_STATUS_CHOICES, blank=False)  # статус чека
    pdf_file = models.FileField(blank=True, null=True, upload_to="pdf")  # ссылка на созданный PDF-файл

    def __str__(self):
        return f"Check {self.pk} - {self.type}"