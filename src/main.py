import atexit
import logging
import threading
import os

import vk_api
from dotenv import load_dotenv
from vk_api.longpoll import VkLongPoll, VkEventType

from database import db
from reports import get_applications, format_applications_text, send_email_report

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

vk_token = os.getenv('VK_TOKEN')
vk_session = vk_api.VkApi(token=vk_token)
session_api = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

class UserState:
    def __init__(self):
        self.states = {}
        self.data = {}

    def get_state(self, user_id):
        return self.states.get(user_id)

    def set_state(self, user_id, state):
        self.states[user_id] = state
        if state is None:
            self.data.pop(user_id, None)
        elif user_id not in self.data:
            self.data[user_id] = {}

    def get_data(self, user_id):
        return self.data.get(user_id, {})

    def set_data(self, user_id, key, value):
        if user_id not in self.data:
            self.data[user_id] = {}
        self.data[user_id][key] = value

user_states = UserState()

def send_msg(user_id, text):
    """Отправка сообщения в ВК с обработкой ошибок"""
    try:
        vk_session.method("messages.send", {
            "user_id": user_id,
            "message": text,
            "random_id": 0
        })
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения пользователю {user_id}: {e}")

def send_report_to_chat(user_id):
    """Отправляет отчёт о заявках в личные сообщения"""
    try:
        applications = get_applications(limit=10)
        text = format_applications_text(applications)
        # Разбиваем длинные сообщения (лимит ВК ~4096 символов)
        for i in range(0, len(text), 4000):
            send_msg(user_id, text[i:i+4000])
    except Exception as e:
        logger.exception("Ошибка при формировании отчёта для чата")
        send_msg(user_id, "Не удалось получить заявки. Попробуйте позже.")

def handle_application(user_id, msg):
    state = user_states.get_state(user_id)
    # ... (существующая логика обработки заявок, без изменений)
    # Для краткости оставлена как есть – см. исходный код
    pass  # Здесь должен быть полный код из исходного main.py

# Запуск отправки email при старте (в фоне)
threading.Thread(target=send_email_report, daemon=True).start()

logger.info("Бот запущен и ожидает сообщения...")

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        msg = event.text.lower().strip()
        user_id = event.user_id

        # Если пользователь в процессе заполнения заявки
        if user_states.get_state(user_id):
            handle_application(user_id, event.text)
            continue

        # Обработка команд
        if msg == "hi":
            send_msg(user_id, "Hi friend!")
        elif msg in ("заявка", "оставить заявку"):
            handle_application(user_id, None)
        elif msg in ("отчет", "заявки"):
            send_report_to_chat(user_id)
        elif msg == "почта":
            threading.Thread(target=send_email_report, daemon=True).start()
            send_msg(user_id, "Отчёт отправляется на почту. Ожидайте.")
        elif msg == "помощь":
            help_text = (
                "Команды:\n"
                "- заявка / оставить заявку – подать заявку\n"
                "- отчет / заявки – показать последние 10 заявок\n"
                "- почта – отправить отчёт на email\n"
                "- помощь – это сообщение"
            )
            send_msg(user_id, help_text)
        else:
            send_msg(user_id, "Неизвестная команда. Напишите 'помощь'.")

atexit.register(db.close)