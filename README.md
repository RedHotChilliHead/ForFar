# ForFar

ForFar — это сервис для генерации чеков для сети ресторанов доставки "ФорФар". 
Сервис позволяет генерировать детализированные чеки для клиентов и сотрудников кухни, 
обеспечивая правильную сборку заказов и улучшение процесса обслуживания.

## Описание проекта

Проект предоставляет REST API для работы с заказами и генерации чеков. Основные функции включают:

1. **Получение заказов**: Сервис принимает заказы от ERP через POST-запрос к API по адресу /forfar/create_checks/. 
API создает чек в базе данных для всех принтеров заведения (статус чека — new).

2. **Постановка задач на генерацию чеков**: API ставит в очередь асинхронные задачи для генерации PDF-файлов чеков. 
Можно также вручную поставить задачу в очередь с помощью функции generate_checks.

3. **Асинхронная генерация PDF**: Воркер Celery берет задачи из очереди и генерирует HTML из Django-шаблона, а затем конвертирует его в PDF-файл (статус чека — rendered) с помощью функции generate_pdf.
Redis используется как брокер задач для Celery.

4. **Получение чеков для печати**: API предоставляет список доступных чеков для печати (со статусом rendered) по адресу /forfar/new_checks/.

5. **Печать чеков**: Приложение позволяет скачать PDF-файл чека по адресу /forfar/check/ и отправить его на печать (статус чека — printed).

## Установка и запуск

Для развертывания всей необходимой инфраструктуры используйте Docker и Docker Compose.

### Предварительные требования

- Убедитесь, что у вас установлены Docker и Docker Compose
- Версия Python: 3.11

### Шаги установки

1. Клонируйте репозиторий проекта:

```
git clone https://github.com/RedHotChilliHead/ForFar.git
cd ForFar
```
2. Установите зависимости:
```
pip install -r requirements.txt
```
3. Запуск Docker-контейнеров:
```
docker volume create postgres_data
docker compose up -d
```
4. Запуск Celery с пулом процессов
```
cd ForFar
celery -A ForFar worker --loglevel=DEBUG -P gevent
```
5. (Необязательно) Запуск Flower для мониторинга задач
```
celery -A ForFar flower
```
Мониторинг будет доступен по адресу http://localhost:5555.
6. Выполнение миграций, создание принтеров и запуск Django сервера
```
cd ForFar
python manage.py migrate
python manage.py create_printers
python manage.py runserver
```
Проект будет доступен по адресу http://localhost:8000/forfar/.

## Использование API

### Создание чека по заказу

Отправьте заказ с помощью POST-запроса к API по адресу /forfar/create_checks/

#### URL

```
POST http://127.0.0.1:8000/forfar/create_checks/
```
#### Пример запроса

```
POST
Content-Type: application/json
Body: {
  "id": 123458,
  "items": [{"name": "Поке с лососем", "quantity": 1, "unit_price": 700}],
  "price": 700,
  "client": {"name": "Ира", "phone": 9173332225},
  "address": "г. Нижний Новгород, ул. Ленина, д. 42",
  "point_id": 3
}
```
Для того, что бы вручную поставить задачу в очередь воспользуйтесь url
`http://127.0.0.1:8000/forfar/generate-checks/1/`, где 1-id чека

- **Успешный ответ**: {"ok": "Чеки успешно созданы"}
- **Ошибки**:
  - {"error": "Для данного заказа уже созданы чеки"}
  - {"error": "Для данной точки не настроено ни одного принтера"}

#### Получение списка доступных чеков для печати

#### URL

```
GET http://127.0.0.1:8000/forfar/new_checks/
```
#### Пример запроса

```
GET http://127.0.0.1:8000/forfar/new_checks/?api_key=generated_api_key_5
```
, где api_key, это уникальный api-ключ принтера

**Ошибки**:
  - в случае указания неправильного api-key в запросе - {"error": "Ошибка авторизации"}

#### Скачивание PDF файла чека для печати

#### URL

```
GET http://127.0.0.1:8000/forfar/check/
```
#### Пример запроса

```
GET http://127.0.0.1:8000/forfar/check/?api_key=generated_api_key_5&check_id=1
```
, где api_key, это уникальный api-ключ принтера, а check_id - первичный ключ чека, предназначенного для печати на этом принтере

**Ошибки**:
- {"error": "Ошибка авторизации"}
- {"error": "Данного чека не существует"}
- {"error": "Для данного чека не сгенерирован PDF-файл"}
- {"error": "PDF-файл не найден"}

### Администратичная панель

Проект предоставляет интерфейс администрирования для управления чеками и принтерами. Административная панель доступна по адресу http://localhost:8000/admin.

- **Логин: admin**
- **Пароль: admin**
