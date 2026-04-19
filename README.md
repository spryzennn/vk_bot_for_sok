# VK Bot for Sok

Бот для ВКонтакте, предназначенный для приема и обработки заявок, с панелью администрирования, уведомлениями и интеграцией с RabbitMQ и email.

## Структура проекта

```
vk_bot_for_sok/
│
├── ApplicationsPublisher/                    # Spring Boot приложение (отдельный проект)
│   ├── src/main/java/com/example/applicationspublisher/applicationspublisher/
│   │   ├── ApplicationsPublisherApplication.java
│   │   ├── config/          # RabbitMQ, CORS, OpenAPI
│   │   ├── controller/      # REST API
│   │   ├── dto/            # Data Transfer Objects
│   │   └── service/        # Сервис публикации в RabbitMQ
│   ├── src/main/resources/application.yaml
│   ├── src/test/java/...   # Тесты JUnit 5
│   ├── pom.xml
│   ├── mvnw
│   └── mvnw.cmd
│
├── vk_bot_for_sok/                         # Основной проект (Python VK бот)
│   ├── src/
│   │   ├── main.py                         # Главный модуль (VK LongPoll + FSM)
│   │   ├── keyboards.py                    # Генерация клавиатур VK (JSON)
│   │   ├── rabbitmq_listener.py            # Слушатель очереди RabbitMQ
│   │   ├── recipients.py                   # Управление админами и email
│   │   └── reports.py                      # Формирование и отправка отчётов
│   │
│   ├── config/
│   │   ├── admin_ids.txt                   # ID администраторов VK
│   │   └── notification_emails.txt         # Email для уведомлений
│   │
│   ├── tests/
│   │   ├── test_main.py
│   │   ├── test_keyboards.py
│   │   ├── test_rabbitmq_listener.py
│   │   ├── test_recipients.py
│   │   └── test_reports.py
│   │
│   ├── .env                                # Переменные окружения
│   ├── requirements.txt
│   └── pytest.ini
│
├── site/                                   # HTML-отчёт о покрытии кода (генерируется pytest-cov)
│   └── index.html
│
├── .gitignore
└── README.md
```

## Модули

### `vk_bot_for_sok/src/main.py`
Основной модуль бота, использующий VK LongPoll для получения сообщений.
- **UserState**: класс для управления состоянием пользователя (FSM)
- Обработчики команд: `hi_command()`, `application_command()`, `report_command()`, `users_list_command()`, `email_command()`, `admin_panel_command()`, `help_command()`
- Обработка заявок: `handle_application()`, `process_application_submission()`
- Вспомогательные функции: `send_msg()`, `remember_user()`, `send_report_to_chat()`

### `vk_bot_for_sok/src/keyboards.py`
Генерация клавиатур для VK API в формате JSON.

### `vk_bot_for_sok/src/rabbitmq_listener.py`
Слушатель очереди RabbitMQ для получения заявок из внешних систем.
- `RabbitMQListener`: класс для прослушивания очереди `applicationsQueue`
- `send_msg()`: отправка сообщений через VK API
- `notify_admins_about_application()`: уведомление администраторов
- `send_email_direct()`: отправка email напрямую
- `process_application()`: обработка входящей заявки

### `vk_bot_for_sok/src/recipients.py`
Управление списками администраторов и email-адресов (файловое хранилище).

### `vk_bot_for_sok/src/reports.py`
Формирование и отправка отчётов по заявкам.

### `ApplicationsPublisher` (отдельный Spring Boot проект)
Принимает заявки через REST API и публикует их в RabbitMQ.
- `ApplicationController`: `POST /api/applications`
- `MessagePublisher`: публикация в очередь `applicationsQueue`
- OpenAPI UI: `http://localhost:8080/swagger-ui.html`

---

## Запуск

### 1. RabbitMQ (Docker)

```bash
docker run -d \
  --name rabbitmq \
  -p 5672:5672 \
  -p 15672:15672 \
  -e RABBITMQ_DEFAULT_USER=user \
  -e RABBITMQ_DEFAULT_PASS=password \
  rabbitmq:3-management
```

Web UI: `http://localhost:15672` (логин: `user`, пароль: `password`)

### 2. ApplicationsPublisher (Spring Boot)

```bash
cd ApplicationsPublisher                    

# Запуск
mvn spring-boot:run        
```

Приложение: `http://localhost:8080`  
Swagger: `http://localhost:8080/swagger-ui.html`

### 3. Python VK бот

```bash
cd vk_bot_for_sok

# Установка зависимостей
pip install -r requirements.txt
```

Настройка `vk_bot_for_sok/.env`:
```env
VK_TOKEN=your_vk_token
ADMIN_ID=your_admin_id
SMTP_SERVER=smtp.gmail.com
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_TO=recipient@example.com
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=user
RABBITMQ_PASSWORD=password
```

Настройка и создание файлов:
- `vk_bot_for_sok/config/admin_ids.txt` — по одному ID администратора на строку
- `vk_bot_for_sok/config/notification_emails.txt` — по одному email на строку

**Запуск бота (VK LongPoll):**
```bash
cd vk_bot_for_sok
python srs/main.py
```

**Запуск слушателя RabbitMQ (отдельный процесс):**
```bash
cd vk_bot_for_sok
python src/rabbitmq_listener.py
```     

### 4. Запуск сайта
```bash
cd site
```

```bash
# Запуск на порту 8000
python -m http.server 8000  
```
## Тестирование

### Python VK бот

Запуск всех тестов с покрытием:
```bash
cd vk_bot_for_sok
python -m pytest --cov=src --cov-report=term-missing
```

Запуск тестов с покрытием:
```bash
python -m pytest vk_bot_for_sok/tests/ --cov=vk_bot_for_sok/src --cov-report=term-missing
```

### ApplicationsPublisher (Spring Boot)

Запуск всех тестов:
```bash
cd ApplicationsPublisher
mvn test
```

Отчёт о покрытии кода (JaCoCo):
```bash
mvn clean test
```

## Архитектура

### Поток данных

```
[Пользователь VK] 
    ↓ (сообщение)
[VK LongPoll - main.py] 
    ↓ (FSM, сохранение в applications[])
[RabbitMQ Listener] 
    ↓ (notify_admins_about_application, send_email_report)
[Администраторы VK] ← [Email через SMTP]
```

```
[Внешняя форма / API]
    ↓ (POST /api/applications)
[ApplicationsPublisher] 
    ↓ (публикация JSON)
[RabbitMQ: applicationsQueue]
    ↓ (потребление)
[rabbitmq_listener.py]
```

### Хранение данных
- **В памяти (Python)**: заявки, состояния пользователей, список пользователей
- **Файлы**: `config/admin_ids.txt`, `config/notification_emails.txt`

## Зависимости

### VK бот (`vk_bot_for_sok/requirements.txt`)
| Библиотека | Назначение |
|------------|------------|
| `vk-api` | Взаимодействие с VK API |
| `python-dotenv` | Загрузка переменных окружения |
| `pika` | Клиент RabbitMQ |
| `pytest` | Тестирование |
| `pytest-cov` | Покрытие кода тестами |

### ApplicationsPublisher (`ApplicationsPublisher/pom.xml`)
| Библиотека | Назначение |
|------------|------------|
| `spring-boot-starter-webmvc` | REST API |
| `spring-boot-starter-amqp` | Интеграция с RabbitMQ |
| `springdoc-openapi-starter-webmvc-ui` | OpenAPI/Swagger |
| `spring-boot-starter-validation` | Валидация DTO |
| `lombok` | Уменьшение шаблонного кода |
| `spring-boot-starter-test` | Тестирование (JUnit 5, Mockito) |
