import json
import logging
import os
import smtplib
import sys
import threading
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv
load_dotenv()

from recipients import get_admin_ids, get_notification_emails

import pika
import vk_api

logger = logging.getLogger(__name__)

QUEUE_NAME = "applicationsQueue"

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', '5672'))
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'user')
RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD', 'password')

SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
EMAIL_TO = os.getenv('EMAIL_TO')
if not SMTP_USER or not SMTP_PASSWORD:
    logger.error("SMTP_USER или SMTP_PASSWORD не найдены в переменных окружения")
    exit(1)

vk_token = os.getenv('VK_TOKEN')
if not vk_token:
    logger.error("VK_TOKEN не найден в переменных окружения")
    exit(1)

logger.info(f"VK_TOKEN loaded: {vk_token[:20]}...")

vk_session = vk_api.VkApi(token=vk_token)
session_api = vk_session.get_api()

try:
    user_info = session_api.users.get()
    logger.info(f"VK API connected successfully, user: {user_info}")
except Exception as e:
    logger.error(f"Не удалось подключиться к VK API: {e}")


def send_msg(user_id, text):
    try:
        params = {
            "user_id": user_id,
            "message": text,
            "random_id": 0
        }
        result = vk_session.method("messages.send", params)
        logger.info(f"Сообщение отправлено пользователю {user_id}, result: {result}")
    except vk_api.exceptions.ApiError as e:
        logger.error(f"VK API Error при отправке пользователю {user_id}: {e}")
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения пользователю {user_id}: {e}")


def notify_admins_about_application(application):
    admin_ids = get_admin_ids(os.getenv('ADMIN_ID'))
    if not admin_ids:
        logger.warning("Нет админов для отправки уведомлений")
        return

    text = (
        "Новая заявка!\n\n"
        f"ФИО: {application.get('fullName', 'не указано')}\n"
        f"Телефон: {application.get('phone', 'не указан')}\n"
        f"Вариант: {application.get('option', 'не указан')}"
    )

    for admin_id in admin_ids:
        try:
            send_msg(int(admin_id), text)
            logger.info(f"Уведомление отправлено админу {admin_id}")
        except Exception as e:
            logger.error(f"Ошибка отправки админу {admin_id}: {e}")


def send_email_direct(application_data):
    """Отправить email напрямую"""
    recipients = get_notification_emails(os.getenv('EMAIL_TO'))
    if not recipients:
        logger.error("Нет получателей email")
        return False
    
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_user = os.getenv('SMTP_USER')
    smtp_pass = os.getenv('SMTP_PASSWORD')
    
    print(f"DEBUG: Отправка email на {recipients}", flush=True)
    print(f"DEBUG: SMTP_SERVER={smtp_server}, SMTP_USER={smtp_user}", flush=True)
    
    if not all([smtp_user, smtp_pass]):
        logger.error("SMTP_USER или SMTP_PASSWORD не заданы")
        return False
    
    try:
        text = f"Новая заявка!\n\nИмя: {application_data.get('name', '-')}\nТелефон: {application_data.get('phone', '-')}\nПримечание: {application_data.get('note', '-')}"
        html = f"<html><body><h2>Новая заявка!</h2><table><tr><td>Имя:</td><td>{application_data.get('name', '-')}</td></tr><tr><td>Телефон:</td><td>{application_data.get('phone', '-')}</td></tr><tr><td>Примечание:</td><td>{application_data.get('note', '-')}</td></tr></table></body></html>"
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Новая заявка!'
        msg['From'] = smtp_user
        msg['To'] = ", ".join(recipients)
        msg.attach(MIMEText(text, 'plain'))
        msg.attach(MIMEText(html, 'html'))
        
        server = smtplib.SMTP(smtp_server, 587)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        
        logger.info(f"Email отправлен на {recipients}")
        print(f"DEBUG: Email успешно отправлен!", flush=True)
        return True
    except Exception as e:
        logger.exception(f"Ошибка отправки email: {e}")
        print(f"DEBUG: Ошибка отправки email: {e}", flush=True)
        return False


def send_email_notification(application, app_id=1):
    try:
        application_data = {
            "id": app_id,
            "name": application.get('fullName', application.get('name', '')),
            "phone": application.get('phone', ''),
            "note": application.get('option', application.get('note', '')),
        }
        logger.info(f"Подготовлены данные для email: {application_data}")
        print(f"DEBUG: Вызов send_email_direct", flush=True)
        result = send_email_direct(application_data)
        logger.info(f"Результат отправки email: {result}")
    except Exception as e:
        logger.error(f"Ошибка отправки email уведомления: {e}")


def process_application(ch, method, properties, body):
    try:
        application = json.loads(body)
        app_id = application.get('id', 1)
        logger.info(f"Получена заявка из очереди: {application}")

        notify_admins_about_application(application)

        logger.info(f"Отправка email на {get_notification_emails(os.getenv('EMAIL_TO'))}")
        threading.Thread(target=send_email_notification, args=(application, app_id), daemon=True).start()

        ch.basic_ack(delivery_tag=method.delivery_tag)
        logger.info("Заявка успешно обработана")
    except Exception as e:
        logger.error(f"Ошибка обработки заявки: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def start_rabbitmq_listener():
    try:
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
        parameters = pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            credentials=credentials
        )
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        channel.queue_declare(queue=QUEUE_NAME, durable=True)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=QUEUE_NAME, on_message_callback=process_application)

        logger.info(f"Слушатель RabbitMQ запущен. Очередь: {QUEUE_NAME}")
        channel.start_consuming()
    except Exception as e:
        logger.error(f"Ошибка запуска слушателя RabbitMQ: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    start_rabbitmq_listener()