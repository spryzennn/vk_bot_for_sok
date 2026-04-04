import logging
import os
import threading
import vk_api
from dotenv import load_dotenv
from vk_api.longpoll import VkLongPoll, VkEventType
from reports import get_applications, format_applications_text, send_email_report, send_new_application_email
from recipients import get_admin_ids
from keyboards import get_main_keyboard, get_main_keyboard_admin, get_application_keyboard, get_application_keyboard_with_skip, get_admin_keyboard, get_cancel_keyboard, get_empty_keyboard

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

vk_token = os.getenv('VK_TOKEN')
admin_id = os.getenv('ADMIN_ID', '710547454')
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
applications = []
known_users = {}

def is_admin(user_id):
    return str(user_id) in get_admin_ids(admin_id)

def get_main_keyboard_for_user(user_id):
    if is_admin(user_id):
        return get_main_keyboard_admin()
    return get_main_keyboard()

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
    if admin_id and str(user_id) != str(admin_id):
        send_msg(user_id, "У вас нет доступа к этой команде.", get_main_keyboard_for_user(user_id))
        return
    try:
        applications = get_applications(limit=10)
        text = format_applications_text(applications)
        for i in range(0, len(text), 4000):
            send_msg(user_id, text[i:i+4000])
    except Exception as e:
        logger.exception("Ошибка при формировании отчёта для чата")
        send_msg(user_id, "Не удалось получить заявки. Попробуйте позже.")


def remember_user(user_id):
    if user_id in known_users:
        return known_users[user_id]
    try:
        response = vk_session.method("users.get", {"user_ids": user_id})
        if response:
            user_info = response[0]
            full_name = f"{user_info.get('first_name', '').strip()} {user_info.get('last_name', '').strip()}".strip()
            known_users[user_id] = full_name or f"Пользователь {user_id}"
        else:
            known_users[user_id] = f"Пользователь {user_id}"
    except Exception as e:
        logger.error(f"Ошибка получения данных пользователя {user_id}: {e}")
        known_users[user_id] = f"Пользователь {user_id}"
    return known_users[user_id]


def format_known_users_text():
    if not known_users:
        return "Пользователи ещё не писали боту."
    lines = ["Список пользователей:"]
    for user_id, full_name in sorted(known_users.items()):
        lines.append(f"- {full_name} — ID: {user_id}")
    return "\n".join(lines)


def send_known_users_to_admin(user_id):
    if not is_admin(user_id):
        send_msg(user_id, "У вас нет доступа к этой команде.", get_main_keyboard_for_user(user_id))
        return
    send_msg(user_id, format_known_users_text(), get_admin_keyboard())


def notify_admin_about_application(application):
    admin_ids = get_admin_ids(admin_id)
    if not admin_ids:
        return
    text = (
        "Новая заявка!\n\n"
        f"Имя: {application['name']}\n"
        f"Телефон: {application['phone']}\n"
        f"Примечание: {application['note'] or 'нет'}"
    )
    for current_admin_id in admin_ids:
        send_msg(current_admin_id, text, get_main_keyboard_for_user(current_admin_id))

def process_application_submission(user_id, application):
    threading.Thread(target=send_new_application_email, args=(application,), daemon=True).start()
    notify_admin_about_application(application)
    send_msg(
        user_id,
        f"Заявка сохранена!\n\nИмя: {application['name']}\nТелефон: {application['phone']}\nПримечание: {application['note'] or 'нет'}",
        get_main_keyboard_for_user(user_id)
    )
    logger.info(
        "Заявка сохранена: user_id=%s, name=%s, phone=%s, note=%s",
        user_id,
        application['name'],
        application['phone'],
        application['note'] or 'нет'
    )


def handle_application(user_id, msg):
    state = user_states.get_state(user_id)
    if state is None:
        user_states.set_state(user_id, "waiting_name")
        send_msg(user_id, "Заполнение заявки\n\nКак вас зовут?", get_application_keyboard())
        return
    if state == "waiting_name":
        if msg.lower() == "отмена":
            user_states.set_state(user_id, None)
            send_msg(user_id, "Заявка отменена.", get_main_keyboard_for_user(user_id))
            return
        user_states.set_data(user_id, "name", msg)
        user_states.set_state(user_id, "waiting_phone")
        send_msg(user_id, f"Отлично, {msg}!\n\nВведите номер телефона:", get_application_keyboard())
    elif state == "waiting_phone":
        if msg.lower() == "отмена":
            user_states.set_state(user_id, None)
            send_msg(user_id, "Заявка отменена.", get_main_keyboard_for_user(user_id))
            return
        user_states.set_data(user_id, "phone", msg)
        user_states.set_state(user_id, "waiting_note")
        send_msg(user_id, f"Номер сохранён!\n\nВведите примечание или нажмите 'Пропустить':", get_application_keyboard_with_skip())
    elif state == "waiting_note":
        if msg.lower() == "отмена":
            user_states.set_state(user_id, None)
            send_msg(user_id, "Заявка отменена.", get_main_keyboard_for_user(user_id))
            return
        note = msg if msg.lower() != "пропустить" else ""
        data = user_states.get_data(user_id)
        application = {
            "id": len(applications) + 1,
            "name": data["name"],
            "phone": data["phone"],
            "note": note,
        }
        applications.append(application)
        user_states.set_state(user_id, None)
        process_application_submission(user_id, application)

logger.info("Бот запущен и ожидает сообщения...")


def main_loop_handler(user_id, msg):
    remember_user(user_id)
    if user_states.get_state(user_id):
        handle_application(user_id, msg)
        return
    if msg == "hi":
        send_msg(user_id, "Привет! Я бот для работы с заявками. Выберите действие:", get_main_keyboard_for_user(user_id))
    elif msg in ("заявка", "оставить заявку"):
        handle_application(user_id, None)
    elif msg in ("отчет", "заявки", "посмотреть заявки"):
        if not is_admin(user_id):
            send_msg(user_id, "У вас нет доступа к этой команде.", get_main_keyboard_for_user(user_id))
        else:
            send_report_to_chat(user_id)
    elif msg in ("почта", "отчет на почту", "отправь по почте заявки"):
        if not is_admin(user_id):
            send_msg(user_id, "У вас нет доступа к этой команде.", get_main_keyboard_for_user(user_id))
        else:
            threading.Thread(target=send_email_report, daemon=True).start()
            send_msg(user_id, "Отчет отправляется на почту. Ожидайте.", get_admin_keyboard())
    elif msg == "список пользователей":
        send_known_users_to_admin(user_id)
    elif msg == "админ" or msg == "панель админа":
        if not is_admin(user_id):
            send_msg(user_id, "У вас нет доступа к админ-панели.", get_main_keyboard_for_user(user_id))
        else:
            send_msg(user_id, "Панель администратора:", get_admin_keyboard())
    elif msg == "назад":
        send_msg(user_id, "Главное меню:", get_main_keyboard_for_user(user_id))
    elif msg == "помощь":
        if is_admin(user_id):
            help_text = (
                "Доступные команды:\n\n"
                "Оставить заявку - подать заявку\n"
                "Панель админа - открыть меню администратора\n"
                "Список пользователей - показать всех пользователей, писавших боту\n"
                "Помощь - это сообщение"
            )
        else:
            help_text = (
                "Доступные команды:\n\n"
                "Оставить заявку - подать заявку\n"
                "Помощь - это сообщение"
            )
        send_msg(user_id, help_text, get_main_keyboard_for_user(user_id))
    else:
        send_msg(user_id, "Неизвестная команда. Напишите 'Помощь' или используйте кнопки.", get_main_keyboard_for_user(user_id))

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        msg = event.text.lower().strip()
        user_id = event.user_id
        main_loop_handler(user_id, msg)

