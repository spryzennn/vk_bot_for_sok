import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from database import create_connection

logger = logging.getLogger(__name__)

def get_applications(limit=10):
    """Возвращает последние заявки (id, name, phone, note)"""
    conn = create_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, phone, note FROM applications ORDER BY id DESC LIMIT %s",
                (limit,)
            )
            return cur.fetchall()
    finally:
        conn.close()

def format_applications_text(applications):
    """Текстовое представление для отправки в ВК"""
    if not applications:
        return "Нет заявок."
    lines = ["Последние заявки:"]
    for app in applications:
        lines.extend([
            f"\nID: {app[0]}",
            f"Имя: {app[1]}",
            f"Телефон: {app[2]}",
            f"Примечание: {app[3] or 'нет'}",
            "-" * 20
        ])
    return "\n".join(lines)

def format_applications_html(applications):
    """HTML‑представление для email"""
    if not applications:
        return "<p>Нет заявок</p>"
    html = """<html>
    <head><style>
        body { font-family: Arial; }
        table { border-collapse: collapse; width: 100%%; }
        th { background: #4CAF50; color: white; padding: 8px; }
        td { border: 1px solid #ddd; padding: 8px; }
        tr:nth-child(even) { background: #f2f2f2; }
    </style></head>
    <body><h2>Последние заявки</h2><table>
        <tr><th>ID</th><th>Имя</th><th>Телефон</th><th>Примечание</th></tr>"""
    for app in applications:
        html += f"<tr><td>{app[0]}</td><td>{app[1]}</td><td>{app[2]}</td><td>{app[3] or ''}</td></tr>"
    html += "</table></body></html>"
    return html

def send_email_report(to_email=None):
    """Отправляет отчёт на почту (параметры из .env)"""
    to_email = to_email or os.getenv('EMAIL_TO')
    if not to_email:
        logger.error("EMAIL_TO не задан в .env")
        return False

    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_user = os.getenv('SMTP_USER')
    smtp_pass = os.getenv('SMTP_PASSWORD')
    if not all([smtp_user, smtp_pass]):
        logger.error("SMTP_USER или SMTP_PASSWORD не заданы")
        return False

    try:
        applications = get_applications(limit=10)
        text_part = MIMEText(format_applications_text(applications), 'plain')
        html_part = MIMEText(format_applications_html(applications), 'html')

        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Отчёт по заявкам'
        msg['From'] = smtp_user
        msg['To'] = to_email
        msg.attach(text_part)
        msg.attach(html_part)

        server = smtplib.SMTP(smtp_server, 587)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        logger.info(f"Email отправлен на {to_email}")
        return True
    except Exception:
        logger.exception("Ошибка отправки email")
        return False