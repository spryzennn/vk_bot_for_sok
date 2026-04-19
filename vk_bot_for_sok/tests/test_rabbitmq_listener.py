import pytest
import json
from unittest.mock import patch, MagicMock, call
import importlib
import sys
import os

# Environment variables will be set by fixture before import

@pytest.fixture
def rl_setup(monkeypatch):
    """Set up environment and all external dependencies for rabbitmq_listener."""
    # Set environment variables required by module
    monkeypatch.setenv('VK_TOKEN', 'test_vk_token')
    monkeypatch.setenv('ADMIN_ID', '123456')
    monkeypatch.setenv('SMTP_USER', 'smtp_user@example.com')
    monkeypatch.setenv('SMTP_PASSWORD', 'smtp_pass')
    monkeypatch.setenv('EMAIL_TO', 'to@example.com')
    monkeypatch.setenv('RABBITMQ_HOST', 'localhost')
    monkeypatch.setenv('RABBITMQ_PORT', '5672')
    monkeypatch.setenv('RABBITMQ_USER', 'rabbit_user')
    monkeypatch.setenv('RABBITMQ_PASSWORD', 'rabbit_pass')

    # Patch external libraries before importing the module
    with patch('vk_api.VkApi') as mock_vk_api, \
         patch('pika.BlockingConnection') as mock_pika, \
         patch('smtplib.SMTP') as mock_smtp, \
         patch('threading.Thread') as mock_thread:

        # Configure VK API mock
        mock_vk_session = MagicMock()
        mock_vk_api.return_value = mock_vk_session
        mock_vk_session.method = MagicMock()
        mock_api = MagicMock()
        mock_vk_session.get_api.return_value = mock_api
        mock_api.users.get.return_value = [{'first_name': 'Test', 'last_name': 'User'}]

        # Configure RabbitMQ mocks
        mock_connection = MagicMock()
        mock_channel = MagicMock()
        mock_pika.return_value = mock_connection
        mock_connection.channel.return_value = mock_channel

        # Configure SMTP mock
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value = mock_smtp_instance

        # Configure threading mock
        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance

        # Now import/reload the module under the patches
        import rabbitmq_listener as rl
        importlib.reload(rl)

        # Patch recipients functions inside the module to avoid file I/O
        monkeypatch.setattr(rl, 'get_admin_ids', lambda default_admin_id=None: ['123456'])
        monkeypatch.setattr(rl, 'get_notification_emails', lambda default_email=None: ['notify@example.com'])

        # Yield the module and key mocks for test usage
        yield {
            'module': rl,
            'mock_vk_api': mock_vk_api,
            'vk_session': rl.vk_session,
            'mock_pika': mock_pika,
            'connection': mock_connection,
            'channel': mock_channel,
            'mock_smtp': mock_smtp,
            'smtp_instance': mock_smtp_instance,
            'mock_thread': mock_thread,
            'thread_instance': mock_thread_instance,
        }


class TestSendMsg:
    def test_send_msg_success(self, rl_setup):
        rl = rl_setup['module']
        mock_method = rl.vk_session.method
        rl.send_msg(123, "Hello")
        mock_method.assert_called_once_with("messages.send", {"user_id": 123, "message": "Hello", "random_id": 0})

    def test_send_msg_vk_api_error(self, rl_setup, caplog):
        rl = rl_setup['module']
        rl.vk_session.method.side_effect = Exception("VK Error")
        with caplog.at_level('ERROR'):
            rl.send_msg(123, "Hello")
        assert any("Ошибка отправки сообщения" in record.message for record in caplog.records)


class TestNotifyAdminsAboutApplication:
    def test_notify_admins_success(self, rl_setup):
        rl = rl_setup['module']
        # send_msg is mocked via vk_session.method
        app = {"fullName": "John", "phone": "+123", "option": "Test"}
        rl.notify_admins_about_application(app)
        # Should call send_msg for each admin (here one admin)
        rl.vk_session.method.assert_called()
        # Check that the message content is correct
        call_args = rl.vk_session.method.call_args
        assert call_args[0][0] == "messages.send"
        sent = call_args[0][1]
        assert sent["user_id"] == 123456  # admin_id from env (int from string)
        assert "Новая заявка!" in sent["message"]
        assert "John" in sent["message"]
        assert "+123" in sent["message"]

    def test_notify_admins_no_admins(self, rl_setup, caplog):
        rl = rl_setup['module']
        # Override get_admin_ids to return empty
        rl.get_admin_ids = lambda default_admin_id=None: []
        app = {"fullName": "John", "phone": "+123", "option": "Test"}
        with caplog.at_level('WARNING'):
            rl.notify_admins_about_application(app)
        # Should log warning and return without calling send_msg
        rl.vk_session.method.assert_not_called()
        assert any("Нет админов для отправки уведомлений" in record.message for record in caplog.records)


class TestSendEmailDirect:
    def test_send_email_direct_success(self, rl_setup):
        rl = rl_setup['module']
        app_data = {"name": "John", "phone": "+123", "note": "Test"}
        result = rl.send_email_direct(app_data)
        assert result is True
        # Verify SMTP used
        smtp_class = rl_setup['mock_smtp']
        smtp_class.assert_called_once_with('smtp.gmail.com', 587)
        smtp_inst = rl_setup['smtp_instance']
        smtp_inst.starttls.assert_called_once()
        smtp_inst.login.assert_called_once_with('smtp_user@example.com', 'smtp_pass')
        smtp_inst.send_message.assert_called_once()
        smtp_inst.quit.assert_called_once()

    def test_send_email_direct_no_recipients(self, rl_setup):
        rl = rl_setup['module']
        rl.get_notification_emails = lambda default_email=None: []
        app_data = {"name": "John", "phone": "+123", "note": "Test"}
        result = rl.send_email_direct(app_data)
        assert result is False
        smtp_class = rl_setup['mock_smtp']
        smtp_class.assert_not_called()

    def test_send_email_direct_smtp_failure(self, rl_setup, caplog):
        rl = rl_setup['module']
        rl_setup['smtp_instance'].send_message.side_effect = Exception("SMTP error")
        app_data = {"name": "John", "phone": "+123", "note": "Test"}
        result = rl.send_email_direct(app_data)
        assert result is False
        # Should log exception
        with caplog.at_level('ERROR'):
            pass  # Already logged inside function; we can check after
        # The function should have attempted to send
        smtp_inst = rl_setup['smtp_instance']
        smtp_inst.send_message.assert_called_once()


class TestSendEmailNotification:
    def test_send_email_notification_calls_direct(self, rl_setup):
        rl = rl_setup['module']
        # Spy on send_email_direct
        original = rl.send_email_direct
        rl.send_email_direct = MagicMock(return_value=True)
        app = {"fullName": "John", "phone": "+123", "option": "Note"}
        rl.send_email_notification(app, app_id=5)
        rl.send_email_direct.assert_called_once_with({
            "id": 5,
            "name": "John",
            "phone": "+123",
            "note": "Note",
        })
        # Restore if needed but not necessary for isolated test


class TestProcessApplication:
    def test_process_application_success(self, rl_setup):
        rl = rl_setup['module']
        # Mock channel, method
        ch = MagicMock()
        method = MagicMock()
        method.delivery_tag = 12345
        body = json.dumps({"id": 1, "fullName": "John", "phone": "+123", "option": "Test"}).encode()
        rl.process_application(ch, method, None, body)
        # Should ack
        ch.basic_ack.assert_called_once_with(delivery_tag=12345)
        # Should have called notify_admins_about_application (which calls send_msg)
        rl.vk_session.method.assert_called()
        # Should have started a thread for email
        rl_setup['mock_thread'].assert_called()
        thread_call = rl_setup['mock_thread'].call_args
        assert thread_call[1]['target'] == rl.send_email_notification
        assert thread_call[1]['daemon'] is True
        # The thread start should be called
        rl_setup['thread_instance'].start.assert_called_once()

    def test_process_application_invalid_json(self, rl_setup):
        rl = rl_setup['module']
        ch = MagicMock()
        method = MagicMock()
        method.delivery_tag = 999
        body = b"not valid json"
        rl.process_application(ch, method, None, body)
        # Should nack (not requeue)
        ch.basic_nack.assert_called_once_with(delivery_tag=999, requeue=False)
        # Should not ack
        ch.basic_ack.assert_not_called()
        # Should not start thread
        rl_setup['mock_thread'].assert_not_called()

    def test_process_application_exception_during_processing(self, rl_setup, monkeypatch):
        rl = rl_setup['module']
        ch = MagicMock()
        method = MagicMock()
        method.delivery_tag = 777
        body = b"{}"
        # Make notify_admins raise exception
        original_notify = rl.notify_admins_about_application
        def fake_notify(app):
            raise RuntimeError("Notification error")
        monkeypatch.setattr(rl, 'notify_admins_about_application', fake_notify)
        rl.process_application(ch, method, None, body)
        ch.basic_nack.assert_called_once_with(delivery_tag=777, requeue=False)


class TestStartRabbitMQListener:
    def test_start_rabbitmq_listener_success(self, rl_setup):
        rl = rl_setup['module']
        # Call the function (it will try to start consuming, which blocks forever)
        # We'll patch start_consuming to raise an exception immediately to exit, or we can just test that it's called.
        # Better: patch channel.start_consuming to just return (or raise) and then call.
        rl_setup['channel'].start_consuming = MagicMock()
        # But start_rabbitmq_listener calls start_consuming without catching; it will exit if we raise to stop.
        # We can let it raise KeyboardInterrupt to exit.
        rl_setup['channel'].start_consuming.side_effect = KeyboardInterrupt()
        try:
            rl.start_rabbitmq_listener()
        except KeyboardInterrupt:
            pass
        # Verify that connection and channel setup was done
        rl_setup['mock_pika'].assert_called_once()
        # Verify credentials
        conn_args = rl_setup['mock_pika'].call_args[1]  # or call_args[0]? It's called with parameters.
        # We can check that a PlainCredentials was created; but simpler: check that channel methods called
        rl_setup['channel'].queue_declare.assert_called_once_with(queue='applicationsQueue', durable=True)
        rl_setup['channel'].basic_qos.assert_called_once_with(prefetch_count=1)
        rl_setup['channel'].basic_consume.assert_called_once_with(queue='applicationsQueue', on_message_callback=rl.process_application)
        rl_setup['channel'].start_consuming.assert_called_once()
