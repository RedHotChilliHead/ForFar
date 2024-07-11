from celery import shared_task
from django.conf import settings
from django.template.loader import render_to_string
import os
import subprocess
from .models import Check

def render_html(check_id):
    check = Check.objects.get(id=check_id)
    context = {
        'check': check,
    }
    if check.type == "client":
        html_content = render_to_string('forfarapp/client_check.html', context)
    elif check.type == "kitchen":
        html_content = render_to_string('forfarapp/kitchen_check.html', context)
    return html_content

def save_html_to_file(html_content, order_id, check_type):
    filename = f"{order_id}_{check_type}.html"
    filepath = os.path.join(settings.MEDIA_ROOT, 'html', filename)

    # Создание директории, если она не существует
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    # Запись HTML в файл
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)
    return filepath


@shared_task()
def generate_pdf(check_id):
    check = Check.objects.get(id=check_id)
    html_content = render_html(check.id)
    html_file_path = save_html_to_file(html_content, check.order['id'], check.type)
    pdf_file_path = os.path.join(settings.MEDIA_ROOT, 'pdf', f"{check.order['id']}_{check.type}.pdf")

    # Проверка и использование абсолютных путей
    html_file_path = os.path.abspath(html_file_path)
    pdf_file_path = os.path.abspath(pdf_file_path)

    command = f'curl -X POST -F "file=@{html_file_path}" http://{settings.WKHTMLTOPDF_HOST}:{settings.WKHTMLTOPDF_PORT}/ -o {pdf_file_path}'
    subprocess.run(command, shell=True, check=True)
    check.pdf_file = pdf_file_path
    check.status = 'rendered'
    check.save()

