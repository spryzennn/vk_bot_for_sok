import atexit
import logging
import threading
import os
import vk_api
from dotenv import load_dotenv
from vk_api.longpoll import VkLongPoll, VkEventType
from database import db
from reports import get_applications, format_applications_text, send_email_report
from keyboards import get_main_keyboard, get_application_keyboard, get_cancel_keyboard, get_empty_keyboard

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

vk_token = os.getenv('VK_TOKEN')
admin_id = os.getenv('ADMIN_ID')
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

def send_msg(user_id, text, keyboard=None):
    try:
        params = {
            "user_id": user_id,
            "message": text,
            "random_id": 0
        }
        if keyboard:
            params["keyboard"] = keyboard
        vk_session.method("messages.send", params)
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения пользователю {user_id}: {e}")

def send_report_to_chat(user_id):
    # Проверка, что пользователь - админ
    if admin_id and str(user_id) != str(admin_id):
        send_msg(user_id, "У вас нет доступа к этой команде.", get_main_keyboard())
        return
    try:
        applications = get_applications(limit=10)
        text = format_applications_text(applications)
        for i in range(0, len(text), 4000):
            send_msg(user_id, text[i:i+4000])
    except Exception as e:
        logger.exception("Ошибка при формировании отчёта для чата")
        send_msg(user_id, "Не удалось получить заявки. Попробуйте позже.")

def handle_application(user_id, msg):
    state = user_states.get_state(user_id)
    if state is None:
        user_states.set_state(user_id, "waiting_name")
        send_msg(user_id, "Заполнение заявки\n\nКак вас зовут?", get_application_keyboard())
        return
    if state == "waiting_name":
        if msg == "отмена":
            user_states.set_state(user_id, None)
            send_msg(user_id, "Заявка отменена.", get_main_keyboard())
            return
        user_states.set_data(user_id, "name", msg)
        user_states.set_state(user_id, "waiting_phone")
        send_msg(user_id, f"Отлично, {msg}!\n\nВведите номер телефона:", get_application_keyboard())
    elif state == "waiting_phone":
        if msg == "отмена":
            user_states.set_state(user_id, None)
            send_msg(user_id, "Заявка отменена.", get_main_keyboard())
            return
        if msg == "пропустить":
            user_states.set_data(user_id, "phone", "")
            user_states.set_state(user_id, "waiting_note")
            send_msg(user_id, "Пропущено!\n\nДобавьте примечание или нажмите 'Пропустить':", get_application_keyboard())
            return
        user_states.set_data(user_id, "phone", msg)
        user_states.set_state(user_id, "waiting_note")
        send_msg(user_id, "Номер сохранён!\n\nДобавьте примечание (например, 'позвоните после 12:00') или нажмите 'Пропустить':", get_application_keyboard())
    elif state == "waiting_note":
        if msg == "отмена":
            user_states.set_state(user_id, None)
            send_msg(user_id, "Заявка отменена.", get_main_keyboard())
            return
        note = msg if msg != "пропустить" else ""
        data = user_states.get_data(user_id)
        db.execute(
            "INSERT INTO applications (name, phone, note) VALUES (%s, %s, %s)",
            (data["name"], data["phone"], note)
        )
        user_states.set_state(user_id, None)
        send_msg(user_id, f"Заявка сохранена!\n\nИмя: {data['name']}\nТелефон: {data['phone']}\nПримечание: {note or 'нет'}", get_main_keyboard())

        threading.Thread(target=send_email_report, daemon=True).start()

logger.info("Бот запущен и ожидает сообщения...")

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        msg = event.text.lower().strip()
        user_id = event.user_id
        if user_states.get_state(user_id):
            handle_application(user_id, event.text)
            continue
        if msg == "hi":
            send_msg(user_id, "Привет! Я бот для работы с заявками. Выберите действие:", get_main_keyboard())
        elif msg in ("заявка", "оставить заявку"):
            handle_application(user_id, None)
        elif msg in ("отчет", "заявки", "посмотреть заявки"):
            send_report_to_chat(user_id)
        elif msg in ("почта", "отчет на почту", "отправь по почте заявки"):
            threading.Thread(target=send_email_report, daemon=True).start()
            send_msg(user_id, "Отчет отправляется на почту. Ожидайте.", get_main_keyboard())
        elif msg == "помощь":
            help_text = (
                "Доступные команды:\n\n"
                "Оставить заявку - подать заявку\n"
                "Посмотреть заявки - показать последние 10 заявок\n"
                "Отчет на почту - отправить отчет на email\n"
                "Помощь - это сообщение"
            )
            send_msg(user_id, help_text, get_main_keyboard())
        else:
            send_msg(user_id, "Неизвестная команда. Напишите 'Помощь' или используйте кнопки.", get_main_keyboard())

atexit.register(db.close)