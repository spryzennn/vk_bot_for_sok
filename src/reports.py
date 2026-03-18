import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from database import create_connection

logger = logging.getLogger(__name__)

def get_applications(limit=10):
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

def get_latest_application():
    """Получить последнюю заявку"""
    conn = create_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, phone, note FROM applications ORDER BY id DESC LIMIT 1"
            )
            result = cur.fetchone()
            return [result] if result else []
    finally:
        conn.close()

def format_applications_text(applications):
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
    if not applications:
        return "<p>Нет заявок</p>"
    html = """<html>
<head><style>
    body { font-family: 'Segoe UI', Arial, sans-serif; background: #f5f5f5; padding: 20px; }
    .container { max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
    .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center; }
    .header h2 { margin: 0; font-size: 24px; }
    .header p { margin: 5px 0 0; opacity: 0.9; font-size: 14px; }
    table { width: 100%; border-collapse: collapse; }
    th { background: #f8f9fa; color: #333; padding: 12px; text-align: left; font-weight: 600; border-bottom: 2px solid #667eea; }
    td { padding: 12px; border-bottom: 1px solid #eee; color: #555; }
    tr:hover { background: #f8f9fa; }
    .id-col { color: #667eea; font-weight: 600; width: 50px; }
    .name-col { font-weight: 500; color: #333; }
    .phone-col { color: #764ba2; }
    .note-col { font-style: italic; color: #888; }
    .empty-note { color: #ccc; font-style: italic; }
    .footer { padding: 15px; text-align: center; color: #999; font-size: 12px; }
</style></head>
<body>
    <div class="container">
        <div class="header">
            <h2>Отчет по заявкам</h2>
            <p>Автоматическая рассылка от VK Bot</p>
        </div>
        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Имя</th>
                    <th>Телефон</th>
                    <th>Примечание</th>
                </tr>
            </thead>
            <tbody>"""
    for app in applications:
        note = app[3] if app[3] else '<span class="empty-note">нет</span>'
        html += f"""            <tr>
                <td class="id-col">{app[0]}</td>
                <td class="name-col">{app[1]}</td>
                <td class="phone-col">{app[2] or '-'}</td>
                <td class="note-col">{note}</td>
            </tr>"""
    html += """        </tbody>
        </table>
        <div class="footer">
            Отправлено автоматически • Всего показано """ + str(len(applications)) + """ заявок
        </div>
    </div>
</body></html>"""
    return html

def send_email_report(to_email=None):
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

def send_new_application_email(to_email=None):
    """Отправить на почту только что полученную заявку"""
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
        application = get_latest_application()
        if not application:
            logger.warning("Нет заявок для отправки")
            return False
        text_part = MIMEText(format_applications_text(application), 'plain')
        html_part = MIMEText(format_applications_html(application), 'html')
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Новая заявка!'
        msg['From'] = smtp_user
        msg['To'] = to_email
        msg.attach(text_part)
        msg.attach(html_part)
        server = smtplib.SMTP(smtp_server, 587)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        logger.info(f"Email о новой заявке отправлен на {to_email}")
        return True
    except Exception:
        logger.exception("Ошибка отправки email о новой заявке")
        return False