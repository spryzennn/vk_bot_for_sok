# VK-bot for SOK

VK-бот для удобного управления заявками с интеграцией RESTful-сервисом, веб-интерфейсом с использованием RabbitMQ.

---

## Структура проекта

```
ApplicationsPublisherRabbitMQ/
├── ApplicationsPublisher/          # Spring Boot приложение (Java)
│   ├── src/main/java/com/example/ApplicationsPublisher/
│   │   ├── controller/              # REST контроллеры
│   │   ├── service/                 # Бизнес-логика
│   │   └── ApplicationsPublisherApplication.java
│   ├── src/main/resources/
│   │   ├── application.yaml         # Конфигурация Spring Boot
│   │   └── application.properties
│   └── pom.xml                      # Maven зависимости
│
├── vk_bot_for_sok/                  # VK бот (Python)
│   ├── src/
│   │   ├── main.py                  # Главный файл бота
│   │   ├── rabbitmq_listener.py     # Прослушивание очередей RabbitMQ
│   │   ├── reports.py               # Генерация отчетов
│   │   ├── recipients.py            # Получатели уведомлений
│   │   ├── keyboards.py             # Клавиатуры VK
│   │   └── static/                  # Статические файлы для сайта (HTML, CSS, JS)
│   ├── config/
│   │   ├── admin_ids.txt            # ID администраторов (по одному на строке)
│   │   └── notification_emails.txt  # Email для уведомлений (по одному на строке)
│   ├── tests/                       # Модульные тесты
│   ├── requirements.txt             # Python зависимости
│   └── .env                         # Переменные окружения
│
└── README.md
```

---

## Запуск проекта

### 1. Запуск RabbitMQ

```bash
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 -e RABBITMQ_DEFAULT_USER=user -e RABBITMQ_DEFAULT_PASS=password rabbitmq:3-management
```

- **AMQP порт**: 5672
- **Management UI**: http://localhost:15672 (логин: user, пароль: password)

---

### 2. Запуск ApplicationsPublisher (Spring Boot)

Требования: **Java 21**, **Maven**

```bash
cd ApplicationsPublisher
mvn spring-boot:run
```

Приложение будет доступно на **http://localhost:8080**

---

### 3. Запуск сайта-интерфейса (Python HTTP Server)

Веб-интерфейс для отображения статусов заявок:

```bash
cd vk_bot_for_sok/src
python -m http.server 8000
```

Сайт будет доступен на **http://localhost:8000**

---

### 4. Запуск VK бота (Python)

Требования: **Python 3.10+**

```bash
cd vk_bot_for_sok
pip install -r requirements.txt
python src/main.py
```

---

## Настройка конфигурации

### Файлы конфигурации

Создайте файлы в `vk_bot_for_sok/config/`:

- **admin_ids.txt** — список ID администраторов VK (по одному на строке)
- **notification_emails.txt** — email адреса для уведомлений (по одному на строке)

### Переменные окружения

Настройте `vk_bot_for_sok/.env`:

```env
VK_TOKEN=your_vk_token
ADMIN_ID=main_admin_id

SMTP_SERVER=smtp.gmail.com
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_TO=recipient@gmail.com

RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=user
RABBITMQ_PASSWORD=password
```

### Конфигурация Spring Boot

Файл `ApplicationsPublisher/src/main/resources/application.yaml`:

```yaml
spring:
  application:
    name: ApplicationsPublisher
  rabbitmq:
    host: localhost
    port: 5672
    username: user
    password: password

server:
  port: 8080
```