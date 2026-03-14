# VK Bot - Бот для работы с заявками

Бот для VK, который принимает заявки от пользователей, сохраняет их в базу данных и отправляет отчеты на email.

## Файлы проекта

### src/main.py

Главный файл бота - точка входа в приложение.

**Функции:**

- `UserState` - класс для хранения состояния пользователя (в процессе заполнения заявки)
- `send_msg(user_id, text, keyboard)` - отправка сообщения пользователю с опциональной клавиатурой
- `send_report_to_chat(user_id)` - отправка последних 10 заявок в чат
- `handle_application(user_id, msg)` - обработка процесса заполнения заявки (имя -> телефон -> примечание)
- Главный цикл `for event in longpoll.listen()` - обработка входящих сообщений

**Команды бота:**

- `Оставить заявку` - начать заполнение заявки
- `Посмотреть заявки` - показать последние 10 заявок
- `Отчет на почту` - отправить отчет на email
- `Помощь` - показать список команд

### src/keyboards.py

Файл с клавиатурами для VK.

**Функции:**

- `get_main_keyboard()` - главное меню с кнопками
- `get_application_keyboard()` - клавиатура для процесса подачи заявки (Пропустить, Отмена)
- `get_cancel_keyboard()` - клавиатура с кнопкой отмены
- `get_empty_keyboard()` - пустая клавиатура (скрыть кнопки)

### src/database.py

Работа с базой данных PostgreSQL.

**Функции:**

- `create_connection()` - создание подключения к БД
- `Database` класс:
  - `execute(query, params)` - выполнение запроса
  - `fetch_one(query, params)` - получение одной строки
  - `fetch_all(query, params)` - получение всех строк
  - `close()` - закрытие подключения

### src/reports.py

Формирование и отправка отчетов.

**Функции:**

- `get_applications(limit)` - получение последних заявок из БД
- `format_applications_text(applications)` - форматирование заявок в текстовый вид
- `format_applications_html(applications)` - форматирование заявок в HTML для email
- `send_email_report(to_email)` - отправка отчета на email

## Работа с проектом

### 1. Создать .env файл

Создать в корневой папке файл `.env` со следующими переменными:

```
VK_TOKEN=токен_группы_vk
DB_HOST=localhost
DB_PORT=5432
DB_NAME=имя_бд
DB_USER=пользователь_бд
DB_PASSWORD=пароль_бд
EMAIL_TO=email_для_отчетов
SMTP_USER=email_отправителя
SMTP_PASSWORD=пароль_приложения
```

### 2. Установить библиотеки

```bash
pip install -r requirements.txt
```

### 3. Создать базу данных

```sql
CREATE TABLE IF NOT EXISTS applications (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    phone VARCHAR(50),
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4. Запустить проект

```bash
cd src
python main.py
```
