from django.urls import path
from forfarapp.views import CheckCreateView, PDFGivinBackerView, generate_checks

app_name = "forfarapp"

urlpatterns = [
    path('create_checks/', CheckCreateView.as_view(), name='create_checks'),  # Создание чеков для заказа
    path('new_checks/', CheckCreateView.as_view(), name='new_checks'),  # список доступных чеков для печати
    path('check/', PDFGivinBackerView.as_view(), name='pdf_check'),  # PDF-файл чека
    # path('generate-checks/', generate_checks, name='generate_checks'),  # маршрут для управления задачами
    path('generate-checks/<int:check_id>/', generate_checks, name='generate_checks'), # для ручной генерации чеков, если понадобится
]
