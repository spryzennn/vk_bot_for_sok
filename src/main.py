import os
from dotenv import load_dotenv
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

load_dotenv()
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
    vk_session.method("messages.send", {
        "user_id": user_id,
        "message": text,
        "random_id": 0
    })


def handle_application(user_id, msg):
    state = user_states.get_state(user_id)

    if state is None:
        user_states.set_state(user_id, "waiting_name")
        send_msg(user_id, "Заполнение заявки\n\nКак вас зовут?")
        return

    if state == "waiting_name":
        user_states.set_data(user_id, "name", msg)
        user_states.set_state(user_id, "waiting_phone")
        send_msg(user_id, f"Отлично, {msg}!\n\nВведите номер телефона:")

    elif state == "waiting_phone":
        user_states.set_data(user_id, "phone", msg)
        user_states.set_state(user_id, "waiting_note")
        send_msg(user_id, "Номер сохранён!\n\nДобавьте примечание (например, 'позвоните после 12:00') или отправьте 'пропустить':")

    elif state == "waiting_note":
        note = msg if msg != "пропустить" else ""
        data = user_states.get_data(user_id)

        db.execute(
            "INSERT INTO applications (name, phone, note) VALUES (%s, %s, %s)",
            (data["name"], data["phone"], note)
        )

        user_states.set_state(user_id, None)
        send_msg(user_id, f"Заявка сохранена!\n\nИмя: {data['name']}\nТелефон: {data['phone']}\nПримечание: {note or 'нет'}")


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            msg = event.text.lower().strip()
            user_id = event.user_id

            if user_states.get_state(user_id):
                handle_application(user_id, event.text)
                continue

            if msg == "hi":
                send_msg(user_id, "Hi friend!")

            elif msg == "заявка" or msg == "оставить заявку":
                handle_application(user_id, None)

            elif msg == "помощь":
                send_msg(user_id, "Команды:\n- заявка / оставить заявку - подать заявку\n- помощь - показать это сообщение")


import atexit
atexit.register(db.close)
