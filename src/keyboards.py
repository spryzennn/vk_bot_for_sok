import json

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
                        "label": "Посмотреть заявки"
                    },
                    "color": "secondary"
                },
                {
                    "action": {
                        "type": "text",
                        "label": "Отчет на почту"
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