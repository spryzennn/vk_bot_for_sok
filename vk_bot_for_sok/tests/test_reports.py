import pytest
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestReports:
    
    def test_format_applications_text_empty(self):
        from reports import format_applications_text
        result = format_applications_text([])
        assert result == "Нет заявок."

    def test_format_applications_text_with_data(self):
        from reports import format_applications_text
        applications = [
            (1, "John Doe", "+1234567890", "Note 1"),
            (2, "Jane Doe", "+0987654321", None)
        ]
        result = format_applications_text(applications)
        assert "Последние заявки:" in result
        assert "ID: 1" in result
        assert "Имя: John Doe" in result
        assert "Телефон: +1234567890" in result
        assert "Примечание: Note 1" in result
        assert "ID: 2" in result
        assert "Примечание: нет" in result

    def test_format_applications_html_empty(self):
        from reports import format_applications_html
        result = format_applications_html([])
        assert result == "<p>Нет заявок</p>"

    def test_format_applications_html_with_data(self):
        from reports import format_applications_html
        applications = [(1, "John Doe", "+1234567890", "Note 1")]
        result = format_applications_html(applications)
        assert "<html>" in result
        assert "Отчет по заявкам" in result
        assert "John Doe" in result
        assert "+1234567890" in result
        assert "Note 1" in result

    def test_format_applications_html_with_empty_note(self):
        from reports import format_applications_html
        applications = [(1, "John Doe", "+1234567890", None)]
        result = format_applications_html(applications)
        assert "empty-note" in result
        assert "нет" in result

    def test_get_applications(self):
        from reports import get_applications
        from reports import set_applications_storage
        storage = [{"id": 1, "name": "John Doe", "phone": "+1234567890", "note": "Note"}]
        set_applications_storage(storage)
        result = get_applications(limit=10)
        assert len(result) == 1
        assert result[0] == (1, "John Doe", "+1234567890", "Note")

    def test_get_latest_application_with_data(self):
        from reports import get_latest_application
        from reports import set_applications_storage
        storage = [{"id": 1, "name": "John Doe", "phone": "+1234567890", "note": "Note"}]
        set_applications_storage(storage)
        result = get_latest_application()
        assert len(result) == 1
        assert result[0] == (1, "John Doe", "+1234567890", "Note")

    def test_get_latest_application_empty(self):
        from reports import get_latest_application
        from reports import set_applications_storage
        set_applications_storage([])
        result = get_latest_application()
        assert result == []

    @patch('reports.get_applications')
    @patch('reports.format_applications_text')
    @patch('reports.format_applications_html')
    @patch('os.getenv')
    def test_send_email_report_no_email(self, mock_getenv, mock_html, mock_text, mock_get_apps):
        from reports import send_email_report
        mock_getenv.side_effect = lambda k, d=None: {
            'EMAIL_TO': None,
            'SMTP_SERVER': 'smtp.gmail.com',
            'SMTP_USER': 'test@test.com',
            'SMTP_PASSWORD': 'password'
        }.get(k, d)
        mock_get_apps.return_value = []
        mock_text.return_value = "Text"
        mock_html.return_value = "<html></html>"
        result = send_email_report()
        assert result is False

    @patch('reports.get_applications')
    @patch('reports.format_applications_text')
    @patch('reports.format_applications_html')
    @patch('os.getenv')
    def test_send_email_report_no_smtp_credentials(self, mock_getenv, mock_html, mock_text, mock_get_apps):
        from reports import send_email_report
        mock_getenv.side_effect = lambda k, d=None: {
            'EMAIL_TO': 'test@test.com',
            'SMTP_SERVER': 'smtp.gmail.com',
            'SMTP_USER': None,
            'SMTP_PASSWORD': None
        }.get(k, d)
        mock_get_apps.return_value = []
        mock_text.return_value = "Text"
        mock_html.return_value = "<html></html>"
        result = send_email_report()
        assert result is False

    @patch('smtplib.SMTP')
    @patch('reports.get_applications')
    @patch('reports.format_applications_text')
    @patch('reports.format_applications_html')
    @patch('os.getenv')
    def test_send_email_report_success(self, mock_getenv, mock_html, mock_text, mock_get_apps, mock_smtp):
        from reports import send_email_report
        mock_getenv.side_effect = lambda k, d=None: {
            'EMAIL_TO': 'test@test.com',
            'SMTP_SERVER': 'smtp.gmail.com',
            'SMTP_USER': 'test@test.com',
            'SMTP_PASSWORD': 'password'
        }.get(k, d)
        mock_get_apps.return_value = [(1, "John", "+123", "Note")]
        mock_text.return_value = "Text"
        mock_html.return_value = "<html>HTML</html>"
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        result = send_email_report()
        assert result is True
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with('test@test.com', 'password')
        mock_server.send_message.assert_called_once()
        mock_server.quit.assert_called_once()

    @patch('reports.get_latest_application')
    @patch('reports.format_applications_text')
    @patch('reports.format_applications_html')
    @patch('os.getenv')
    def test_send_new_application_email_no_email(self, mock_getenv, mock_html, mock_text, mock_get_apps):
        from reports import send_new_application_email
        mock_getenv.side_effect = lambda k, d=None: {
            'EMAIL_TO': None,
            'SMTP_SERVER': 'smtp.gmail.com',
            'SMTP_USER': 'test@test.com',
            'SMTP_PASSWORD': 'password'
        }.get(k, d)
        mock_get_apps.return_value = []
        mock_text.return_value = "Text"
        mock_html.return_value = "<html></html>"
        result = send_new_application_email()
        assert result is False

    @patch('reports.get_latest_application')
    @patch('reports.format_applications_text')
    @patch('reports.format_applications_html')
    @patch('os.getenv')
    def test_send_new_application_email_no_applications(self, mock_getenv, mock_html, mock_text, mock_get_apps):
        from reports import send_new_application_email
        mock_getenv.side_effect = lambda k, d=None: {
            'EMAIL_TO': 'test@test.com',
            'SMTP_SERVER': 'smtp.gmail.com',
            'SMTP_USER': 'test@test.com',
            'SMTP_PASSWORD': 'password'
        }.get(k, d)
        mock_get_apps.return_value = []
        mock_text.return_value = "Text"
        mock_html.return_value = "<html></html>"
        result = send_new_application_email()
        assert result is False

    @patch('smtplib.SMTP')
    @patch('reports.get_latest_application')
    @patch('reports.format_applications_text')
    @patch('reports.format_applications_html')
    @patch('os.getenv')
    def test_send_new_application_email_success(self, mock_getenv, mock_html, mock_text, mock_get_apps, mock_smtp):
        from reports import send_new_application_email
        mock_getenv.side_effect = lambda k, d=None: {
            'EMAIL_TO': 'test@test.com',
            'SMTP_SERVER': 'smtp.gmail.com',
            'SMTP_USER': 'test@test.com',
            'SMTP_PASSWORD': 'password'
        }.get(k, d)
        mock_get_apps.return_value = [(1, "John", "+123", "Note")]
        mock_text.return_value = "Text"
        mock_html.return_value = "<html>HTML</html>"
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        result = send_new_application_email()
        assert result is True
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with('test@test.com', 'password')
        mock_server.send_message.assert_called_once()
        mock_server.quit.assert_called_once()

    @patch('smtplib.SMTP')
    @patch('reports.get_applications')
    @patch('reports.format_applications_text')
    @patch('reports.format_applications_html')
    @patch('os.getenv')
    def test_send_email_report_exception(self, mock_getenv, mock_html, mock_text, mock_get_apps, mock_smtp):
        from reports import send_email_report
        mock_getenv.side_effect = lambda k, d=None: {
            'EMAIL_TO': 'test@test.com',
            'SMTP_SERVER': 'smtp.gmail.com',
            'SMTP_USER': 'test@test.com',
            'SMTP_PASSWORD': 'password'
        }.get(k, d)
        mock_get_apps.return_value = [(1, 'John', '+123', 'Note')]
        mock_text.return_value = 'Text'
        mock_html.return_value = '<html>HTML</html>'
        mock_server = MagicMock()
        mock_server.login.side_effect = Exception('SMTP error')
        mock_smtp.return_value = mock_server
        result = send_email_report()
        assert result is False

    @patch('smtplib.SMTP')
    @patch('reports.get_applications')
    @patch('reports.format_applications_text')
    @patch('reports.format_applications_html')
    @patch('os.getenv')
    def test_send_email_report_empty(self, mock_getenv, mock_html, mock_text, mock_get_apps, mock_smtp):
        from reports import send_email_report
        mock_getenv.side_effect = lambda k, d=None: {
            'EMAIL_TO': 'test@test.com',
            'SMTP_SERVER': 'smtp.gmail.com',
            'SMTP_USER': 'test@test.com',
            'SMTP_PASSWORD': 'password'
        }.get(k, d)
        mock_get_apps.return_value = []
        mock_text.return_value = 'Нет заявок.'
        mock_html.return_value = '<p>Нет заявок</p>'
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        result = send_email_report()
        assert result is True
        mock_server.send_message.assert_called_once()

    @patch('smtplib.SMTP')
    @patch('reports.get_latest_application')
    @patch('reports.format_applications_text')
    @patch('reports.format_applications_html')
    @patch('os.getenv')
    def test_send_new_application_email_exception(self, mock_getenv, mock_html, mock_text, mock_get_apps, mock_smtp):
        from reports import send_new_application_email
        mock_getenv.side_effect = lambda k, d=None: {
            'EMAIL_TO': 'test@test.com',
            'SMTP_SERVER': 'smtp.gmail.com',
            'SMTP_USER': 'test@test.com',
            'SMTP_PASSWORD': 'password'
        }.get(k, d)
        mock_get_apps.return_value = [(1, 'John', '+123', 'Note')]
        mock_text.return_value = 'Text'
        mock_html.return_value = '<html>HTML</html>'
        mock_server = MagicMock()
        mock_server.login.side_effect = Exception('SMTP error')
        mock_smtp.return_value = mock_server
        result = send_new_application_email()
        assert result is False
