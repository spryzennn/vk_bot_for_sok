import json
import os
from dotenv import load_dotenv

load_dotenv()

ADMIN_ID = os.getenv('ADMIN_ID')

def get_main_keyboard():
    keyboard = {
        "one_time": False,
        "buttons": [
            [
                {
                    "action": {
                        "type": "text",
                        "label": "Оставить заявку"
                    },
                    "color": "primary"
                }
            ],
            [
                {
                    "action": {
                        "type": "text",
                        "label": "Панель админа"
                    },
                    "color": "secondary"
                }
            ],
            [
                {
                    "action": {
                        "type": "text",
                        "label": "Помощь"
                    },
                    "color": "default"
                }
            ]
        ]
    }
    return json.dumps(keyboard)

def get_main_keyboard_admin():
    keyboard = {
        "one_time": False,
        "buttons": [
            [
                {
                    "action": {
                        "type": "text",
                        "label": "Оставить заявку"
                    },
                    "color": "primary"
                }
            ],
            [
                {
                    "action": {
                        "type": "text",
                        "label": "Панель админа"
                    },
                    "color": "secondary"
                }
            ],
            [
                {
                    "action": {
                        "type": "text",
                        "label": "Помощь"
                    },
                    "color": "default"
                }
            ]
        ]
    }
    return json.dumps(keyboard)

def get_application_keyboard():
    keyboard = {
        "one_time": True,
        "buttons": [
            [
                {
                    "action": {
                        "type": "text",
                        "label": "Отмена"
                    },
                    "color": "negative"
                }
            ]
        ]
    }
    return json.dumps(keyboard)

def get_application_keyboard_with_skip():
    keyboard = {
        "one_time": True,
        "buttons": [
            [
                {
                    "action": {
                        "type": "text",
                        "label": "Пропустить"
                    },
                    "color": "default"
                }
            ],
            [
                {
                    "action": {
                        "type": "text",
                        "label": "Отмена"
                    },
                    "color": "negative"
                }
            ]
        ]
    }
    return json.dumps(keyboard)

def get_cancel_keyboard():
    keyboard = {
        "one_time": True,
        "buttons": [
            [
                {
                    "action": {
                        "type": "text",
                        "label": "Отмена"
                    },
                    "color": "negative"
                }
            ]
        ]
    }
    return json.dumps(keyboard)

def get_empty_keyboard():
    return json.dumps({"buttons": []})

def get_admin_keyboard():
    keyboard = {
        "one_time": False,
        "buttons": [
            [
                {
                    "action": {
                        "type": "text",
                        "label": "Список пользователей"
                    },
                    "color": "primary"
                }
            ],
            [
                {
                    "action": {
                        "type": "text",
                        "label": "Список почт"
                    },
                    "color": "primary"
                }
            ],
            [
                {
                    "action": {
                        "type": "text",
                        "label": "Добавить админа"
                    },
                    "color": "secondary"
                }
            ],
            [
                {
                    "action": {
                        "type": "text",
                        "label": "Удалить админа"
                    },
                    "color": "secondary"
                }
            ],
            [
                {
                    "action": {
                        "type": "text",
                        "label": "Добавить почту"
                    },
                    "color": "secondary"
                }
            ],
            [
                {
                    "action": {
                        "type": "text",
                        "label": "Удалить почту"
                    },
                    "color": "secondary"
                }
            ],
            [
                {
                    "action": {
                        "type": "text",
                        "label": "Отмена"
                    },
                    "color": "negative"
                }
            ],
            [
                {
                    "action": {
                        "type": "text",
                        "label": "Назад"
                    },
                    "color": "default"
                }
            ]
        ]
    }
    return json.dumps(keyboard)
