from django.contrib import admin
from .models import Check, Printer

@admin.register(Check)
class PostAdmin(admin.ModelAdmin):
    """
    Настройка отображения модели Check - чеков
    """
    ordering = ('pk',)  # сортировка
    list_display = "pk", "printer", "type", "status"
    list_filter = ('printer', 'type', 'status')
    list_display_links = "pk", "printer"


@admin.register(Printer)
class PostAdmin(admin.ModelAdmin):
    """
    Настройка отображения модели Printer - принтеров
    """
    ordering = ('pk',)  # сортировка
    list_display = "pk", "name", "api_key", "check_type", "point_id"
    list_display_links = "pk", "name", "api_key"
    list_filter = ('check_type', 'point_id')

