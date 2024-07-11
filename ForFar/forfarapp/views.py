import os

from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from django.http import FileResponse
from rest_framework import status

from forfarapp.models import Check, Printer
from forfarapp.serializers import CheckSerializer

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .tasks import generate_pdf


class CheckCreateView(APIView):
    def post(self, request: Request) -> Response:
        """
        Метод обработки POST-запроса ERP к API, который создает чеки с использованием информации из полученного JSON
        {"id": 123457,
    "items": {"name": "Поке", "quantity": 2, "unit_price": 700},
    "price": 1400, "client": {"name": "Ира", "phone": 9173332223},
    "address": "г. Уфа, ул. Ленина, д. 42", "point_id": 2}
        """
        order = request.data
        checks = Check.objects.filter(order=order)
        point_id = request.data.get('point_id')
        printers = Printer.objects.filter(point_id=point_id)

        if checks:
            return Response({"error": "Для данного заказа уже созданы чеки"}, status=status.HTTP_400_BAD_REQUEST)

        if not printers:
            return Response({"error": "Для данной точки не настроено ни одного принтера"},
                            status=status.HTTP_400_BAD_REQUEST)

        checks = []
        for printer in printers:
            check = Check.objects.create(printer_id=printer.pk,
                                 type=printer.check_type,
                                 order=order,
                                 status='new')
            checks.append(check)

        # Вызов функции для постановки задач в очередь
        for check in checks:
            generate_pdf.delay(check.id)

        return Response({"ok": "Чеки успешно созданы"}, status=status.HTTP_200_OK)

    def get(self, request: Request) -> Response:
        """
        Метод обработки GET-запроса приложения к API, который отображает список доступных чеков для печати
        Обязательный параметр api_key: например, http://127.0.0.1:8000/forfar/new_checks/?api_key=generated_api_key_1
        """
        api_key = request.query_params.get('api_key')
        try:
            printer = Printer.objects.get(api_key=api_key)
        except Printer.DoesNotExist:
            return Response({"error": "Ошибка авторизации"}, status=status.HTTP_401_UNAUTHORIZED)

        queryset = Check.objects.filter(status='rendered', printer=printer.pk)
        serializer = CheckSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PDFGivinBackerView(APIView):
    def get(self, request: Request) -> Response:
        """
        Метод обработки GET-запроса приложения к API, который отдает готовый PDF-файл чека
        Обязательные параметры: api_key и check_id,
        например, http://127.0.0.1:8000/forfar/check/?api_key=generated_api_key_1&check_id=1
        """
        api_key = request.query_params.get('api_key')
        check_id = request.query_params.get('check_id')
        try:
            printer = Printer.objects.get(api_key=api_key)
            check = Check.objects.get(pk=check_id)
        except Printer.DoesNotExist:
            return Response({"error": "Ошибка авторизации"}, status=status.HTTP_401_UNAUTHORIZED)
        except Check.DoesNotExist:
            return Response({"error": "Данного чека не существует"}, status=status.HTTP_400_BAD_REQUEST)

        if check.pdf_file is None:
            return Response({"error": "Для данного чека не сгенерирован PDF-файл"}, status=status.HTTP_400_BAD_REQUEST)

        check.status = 'printed'
        check.save()

        try:
            pdf_file_path = check.pdf_file.path  # Получаем строку пути к файлу
            response = FileResponse(open(pdf_file_path, 'rb'), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(pdf_file_path)}"'
            return response
        except FileNotFoundError:
            return Response({"error": "PDF-файл не найден"}, status=status.HTTP_404_NOT_FOUND)


def generate_checks(request, check_id):
    """
    Функция, которая будет ставить задачи в очередь
    """
    check = get_object_or_404(Check, id=check_id)
    print('check_id=', check_id)
    generate_pdf.delay(check_id)  # Ставим задачу в очередь
    print('Ставим задачу в очередь')
    return JsonResponse({'status': 'PDF generation task queued.'})
