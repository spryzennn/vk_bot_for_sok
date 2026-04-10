import pytest
import sys
import os
from unittest.mock import patch, MagicMock, call

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

os.environ['ADMIN_ID'] = '123456789'


class TestUserState:
    def test_user_state_init(self):
        from main import UserState
        state = UserState()
        assert state.states == {}
        assert state.data == {}

    def test_get_state_none(self):
        from main import UserState
        state = UserState()
        result = state.get_state(123)
        assert result is None

    def test_get_state_existing(self):
        from main import UserState
        state = UserState()
        state.states[123] = "waiting_name"
        result = state.get_state(123)
        assert result == "waiting_name"

    def test_set_state_with_value(self):
        from main import UserState
        state = UserState()
        state.set_state(123, "waiting_name")
        assert state.states[123] == "waiting_name"
        assert state.data[123] == {}

    def test_set_state_to_none_clears_data(self):
        from main import UserState
        state = UserState()
        state.states[123] = "waiting_name"
        state.data[123] = {"name": "John"}
        state.set_state(123, None)
        assert state.states[123] is None
        assert 123 not in state.data

    def test_get_data_none(self):
        from main import UserState
        state = UserState()
        result = state.get_data(123)
        assert result == {}

    def test_get_data_existing(self):
        from main import UserState
        state = UserState()
        state.data[123] = {"name": "John"}
        result = state.get_data(123)
        assert result == {"name": "John"}

    def test_set_data_new_user(self):
        from main import UserState
        state = UserState()
        state.set_data(123, "name", "John")
        assert state.data[123] == {"name": "John"}

    def test_set_data_existing_user(self):
        from main import UserState
        state = UserState()
        state.data[123] = {"name": "John"}
        state.set_data(123, "phone", "+1234567890")
        assert state.data[123] == {"name": "John", "phone": "+1234567890"}


class TestMainFunctions:
    
    @patch('os.getenv')
    def test_is_admin_true(self, mock_getenv):
        from main import is_admin
        mock_getenv.return_value = '123456789'
        result = is_admin(123456789)
        assert result is True

    @patch('os.getenv')
    def test_is_admin_false(self, mock_getenv):
        from main import is_admin
        mock_getenv.return_value = '123456789'
        result = is_admin(987654321)
        assert result is False

    @patch('os.getenv')
    def test_is_admin_no_admin_id(self, mock_getenv):
        from main import is_admin
        mock_getenv.return_value = None
        result = is_admin(123456789)
        assert result is False

    @patch('main.get_main_keyboard')
    @patch('main.get_main_keyboard_admin')
    @patch('main.is_admin')
    def test_get_main_keyboard_for_user_admin(self, mock_is_admin, mock_admin_kb, mock_user_kb):
        from main import get_main_keyboard_for_user
        mock_is_admin.return_value = True
        mock_admin_kb.return_value = 'admin_kb'
        mock_user_kb.return_value = 'user_kb'
        result = get_main_keyboard_for_user(123456789)
        assert result == 'admin_kb'

    @patch('main.get_main_keyboard')
    @patch('main.get_main_keyboard_admin')
    @patch('main.is_admin')
    def test_get_main_keyboard_for_user_regular(self, mock_is_admin, mock_admin_kb, mock_user_kb):
        from main import get_main_keyboard_for_user
        mock_is_admin.return_value = False
        mock_admin_kb.return_value = 'admin_kb'
        mock_user_kb.return_value = 'user_kb'
        result = get_main_keyboard_for_user(123456789)
        assert result == 'user_kb'

    @patch('main.vk_session')
    def test_send_msg_without_keyboard(self, mock_vk_session):
        from main import send_msg
        mock_method = MagicMock()
        mock_vk_session.method = mock_method
        send_msg(123, "Hello")
        mock_method.assert_called_once()
        call_args = mock_method.call_args
        assert call_args[0][0] == "messages.send"
        assert call_args[1]['user_id'] == 123
        assert call_args[1]['message'] == "Hello"
        assert call_args[1]['random_id'] == 0

    @patch('main.vk_session')
    def test_send_msg_with_keyboard(self, mock_vk_session):
        from main import send_msg
        mock_method = MagicMock()
        mock_vk_session.method = mock_method
        send_msg(123, "Hello", '{"keyboard": "test"}')
        call_args = mock_method.call_args
        assert call_args[1]['keyboard'] == '{"keyboard": "test"}'

    @patch('main.vk_session')
    @patch('main.logger')
    def test_send_msg_exception(self, mock_logger, mock_vk_session):
        from main import send_msg
        mock_method = MagicMock(side_effect=Exception("Error"))
        mock_vk_session.method = mock_method
        send_msg(123, "Hello")
        mock_logger.error.assert_called_once()

    @patch('main.vk_session')
    def test_remember_user(self, mock_vk_session):
        from main import remember_user
        from main import known_users
        known_users.clear()
        mock_vk_session.method.return_value = [{"first_name": "Иван", "last_name": "Иванов"}]
        result = remember_user(123)
        assert result == "Иван Иванов"
        assert known_users[123] == "Иван Иванов"

    def test_format_known_users_text(self):
        from main import format_known_users_text
        from main import known_users
        known_users.clear()
        known_users[123] = "Иван Иванов"
        known_users[456] = "Петр Петров"
        result = format_known_users_text()
        assert "Список пользователей:" in result
        assert "Иван Иванов — ID: 123" in result
        assert "Петр Петров — ID: 456" in result


class TestHandleApplication:
    
    @patch('main.send_msg')
    @patch('main.get_application_keyboard')
    def test_handle_application_new(self, mock_kb, mock_send_msg):
        from main import handle_application
        from main import user_states
        user_states.states = {}
        user_states.data = {}
        mock_kb.return_value = 'app_kb'
        handle_application(123, "Hello")
        assert user_states.get_state(123) == "waiting_name"
        mock_send_msg.assert_called_once_with(123, "Заполнение заявки\n\nКак вас зовут?", 'app_kb')

    @patch('main.send_msg')
    @patch('main.get_application_keyboard')
    def test_handle_application_waiting_name_cancel(self, mock_kb, mock_send_msg):
        from main import handle_application
        from main import user_states
        user_states.set_state(123, "waiting_name")
        user_states.set_data(123, "name", "John")
        mock_kb.return_value = 'app_kb'
        handle_application(123, "отмена")
        assert user_states.get_state(123) is None
        mock_send_msg.assert_called_once()

    @patch('main.send_msg')
    @patch('main.get_application_keyboard')
    def test_handle_application_waiting_name_set_name(self, mock_kb, mock_send_msg):
        from main import handle_application
        from main import user_states
        user_states.set_state(123, "waiting_name")
        user_states.set_data(123, "name", "")
        mock_kb.return_value = 'app_kb'
        handle_application(123, "John Doe")
        assert user_states.get_state(123) == "waiting_phone"
        assert user_states.get_data(123)["name"] == "John Doe"

    @patch('main.send_msg')
    @patch('main.get_application_keyboard')
    def test_handle_application_waiting_phone_cancel(self, mock_kb, mock_send_msg):
        from main import handle_application
        from main import user_states
        user_states.set_state(123, "waiting_phone")
        user_states.set_data(123, "name", "John")
        mock_kb.return_value = 'app_kb'
        handle_application(123, "отмена")
        assert user_states.get_state(123) is None

    @patch('main.send_msg')
    @patch('main.get_application_keyboard')
    def test_handle_application_waiting_phone_set_phone(self, mock_kb, mock_send_msg):
        from main import handle_application
        from main import user_states
        user_states.set_state(123, "waiting_phone")
        user_states.set_data(123, "name", "John")
        mock_kb.return_value = 'app_kb'
        handle_application(123, "+1234567890")
        assert user_states.get_state(123) == "waiting_note"
        assert user_states.get_data(123)["phone"] == "+1234567890"

    @patch('main.send_msg')
    @patch('main.get_application_keyboard_with_skip')
    def test_handle_application_waiting_note_cancel(self, mock_kb, mock_send_msg):
        from main import handle_application
        from main import user_states
        user_states.set_state(123, "waiting_note")
        user_states.set_data(123, "name", "John")
        user_states.set_data(123, "phone", "+123")
        mock_kb.return_value = 'app_kb'
        handle_application(123, "отмена")
        assert user_states.get_state(123) is None

    @patch('main.logger')
    @patch('main.send_msg')
    @patch('main.get_main_keyboard_for_user')
    @patch('main.get_application_keyboard_with_skip')
    @patch('main.send_new_application_email')
    def test_handle_application_waiting_note_with_note(self, mock_email, mock_kb, mock_main_kb, mock_send_msg, mock_logger):
        from main import handle_application
        from main import applications
        from main import user_states
        applications.clear()
        user_states.set_state(123, "waiting_note")
        user_states.set_data(123, "name", "John")
        user_states.set_data(123, "phone", "+123")
        mock_kb.return_value = 'app_kb'
        mock_main_kb.return_value = 'main_kb'
        handle_application(123, "Some note")
        assert len(applications) == 1
        assert applications[0]["note"] == "Some note"
        assert user_states.get_state(123) is None
        mock_email.assert_called_once_with(applications[0])
        assert mock_send_msg.call_count == 2
        mock_logger.info.assert_called_once()

    @patch('main.send_msg')
    @patch('main.get_main_keyboard_for_user')
    @patch('main.get_application_keyboard_with_skip')
    @patch('main.send_new_application_email')
    def test_handle_application_waiting_note_skip(self, mock_email, mock_kb, mock_main_kb, mock_send_msg):
        from main import handle_application
        from main import applications
        from main import user_states
        applications.clear()
        user_states.set_state(123, "waiting_note")
        user_states.set_data(123, "name", "John")
        user_states.set_data(123, "phone", "+123")
        mock_kb.return_value = 'app_kb'
        mock_main_kb.return_value = 'main_kb'
        handle_application(123, "Пропустить")
        assert len(applications) == 1
        assert applications[0]["note"] == ""

    @patch('main.send_msg')
    @patch('main.get_main_keyboard_for_user')
    def test_notify_admin_about_application(self, mock_main_kb, mock_send_msg):
        from main import notify_admin_about_application
        application = {
            "id": 1,
            "name": "John",
            "phone": "+123",
            "note": "Test note",
        }
        mock_main_kb.return_value = 'admin_kb'

        notify_admin_about_application(application)

        mock_send_msg.assert_called_once_with(
            '710547454',
            "Новая заявка!\n\nИмя: John\nТелефон: +123\nПримечание: Test note",
            'admin_kb'
        )

    @patch('main.threading.Thread')
    @patch('main.logger')
    @patch('main.send_msg')
    @patch('main.get_main_keyboard_for_user')
    @patch('main.notify_admin_about_application')
    def test_process_application_submission(self, mock_notify_admin, mock_main_kb, mock_send_msg, mock_logger, mock_thread):
        from main import process_application_submission

        application = {
            "id": 1,
            "name": "John",
            "phone": "+123",
            "note": "Test note",
        }
        mock_main_kb.return_value = 'main_kb'
        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance

        process_application_submission(123, application)

        mock_thread.assert_called_once()
        mock_thread_instance.start.assert_called_once()
        mock_notify_admin.assert_called_once_with(application)
        mock_send_msg.assert_called_once_with(
            123,
            "Заявка сохранена!\n\nИмя: John\nТелефон: +123\nПримечание: Test note",
            'main_kb'
        )
        mock_logger.info.assert_called_once()

    @patch('main.send_msg')
    @patch('main.get_admin_keyboard')
    @patch('main.is_admin')
    def test_send_known_users_to_admin(self, mock_is_admin, mock_admin_kb, mock_send_msg):
        from main import send_known_users_to_admin
        from main import known_users
        known_users[710547454] = "Арсен Сосян"
        known_users[540047989] = "Санёк Барабошин"
        mock_is_admin.return_value = True
        mock_admin_kb.return_value = 'admin_kb'
        send_known_users_to_admin(710547454)
        expected = "Список пользователей:\n- Арсен Сосян — ID: 710547454\n- Санёк Барабошин — ID: 540047989"
        mock_send_msg.assert_called_once_with(710547454, expected, 'admin_kb')


class TestSendReportToChat:
    
    @patch('main.send_msg')
    @patch('main.get_main_keyboard_for_user')
    @patch('main.is_admin')
    def test_send_report_to_chat_not_admin(self, mock_is_admin, mock_get_kb, mock_send_msg):
        from main import send_report_to_chat
        mock_is_admin.return_value = False
        mock_get_kb.return_value = 'user_kb'
        send_report_to_chat(123)
        mock_send_msg.assert_called_once_with(123, "У вас нет доступа к этой команде.", 'user_kb')

    @patch('main.send_msg')
    @patch('main.format_applications_text')
    @patch('main.get_applications')
    @patch('main.is_admin')
    def test_send_report_to_chat_admin_success(self, mock_is_admin, mock_get_apps, mock_format, mock_send_msg):
        from main import send_report_to_chat
        mock_is_admin.return_value = True
        mock_get_apps.return_value = [(1, "John", "+123", "Note")]
        mock_format.return_value = "Report text"
        send_report_to_chat(123)
        mock_send_msg.assert_called_once_with(123, "Report text")

    @patch('main.send_msg')
    @patch('main.get_applications')
    @patch('main.is_admin')
    @patch('main.logger')
    def test_send_report_to_chat_exception(self, mock_logger, mock_is_admin, mock_get_apps, mock_send_msg):
        from main import send_report_to_chat
        mock_is_admin.return_value = True
        mock_get_apps.side_effect = Exception("DB Error")
        send_report_to_chat(123)
        mock_logger.exception.assert_called_once()
        mock_send_msg.assert_called_once_with(123, "Не удалось получить заявки. Попробуйте позже.")

    @patch('main.send_msg')
    @patch('main.get_applications')
    @patch('main.is_admin')
    def test_send_report_to_chat_long_text_split(self, mock_is_admin, mock_get_apps, mock_send_msg):
        from main import send_report_to_chat
        mock_is_admin.return_value = True
        long_text = "a" * 5000
        mock_get_apps.return_value = [(1, "John", "+123", "Note")]
        mock_format = MagicMock(return_value=long_text)
        
        with patch('main.format_applications_text', mock_format):
            send_report_to_chat(123)
            assert mock_send_msg.call_count == 2


class TestMainLoopCommands:
    
    @patch('main.remember_user')
    @patch('main.send_msg')
    @patch('main.get_main_keyboard_for_user')
    @patch('main.user_states.get_state')
    def test_hi_command(self, mock_get_state, mock_get_kb, mock_send_msg, mock_remember_user):
        from main import main_loop_handler
        mock_get_state.return_value = None
        mock_get_kb.return_value = 'main_kb'
        
        with patch('main.handle_application') as mock_handle:
            main_loop_handler(123, 'hi')
            mock_send_msg.assert_called_once_with(123, 'Привет! Я бот для работы с заявками. Выберите действие:', 'main_kb')
            mock_handle.assert_not_called()

    @patch('main.remember_user')
    @patch('main.handle_application')
    @patch('main.send_msg')
    @patch('main.get_main_keyboard_for_user')
    @patch('main.user_states.get_state')
    def test_application_command(self, mock_get_state, mock_get_kb, mock_send_msg, mock_handle, mock_remember_user):
        from main import main_loop_handler
        mock_get_state.return_value = None
        mock_get_kb.return_value = 'main_kb'
        
        main_loop_handler(123, 'заявка')
        mock_handle.assert_called_once_with(123, None)
        
        main_loop_handler(123, 'оставить заявку')
        assert mock_handle.call_count == 2

    @patch('main.remember_user')
    @patch('main.send_report_to_chat')
    @patch('main.send_msg')
    @patch('main.get_main_keyboard_for_user')
    @patch('main.is_admin')
    @patch('main.user_states.get_state')
    def test_report_command_admin(self, mock_get_state, mock_is_admin, mock_get_kb, mock_send_msg, mock_send_report, mock_remember_user):
        from main import main_loop_handler
        mock_get_state.return_value = None
        mock_is_admin.return_value = True
        
        main_loop_handler(123, 'отчет')
        mock_send_report.assert_called_once_with(123)
        
        main_loop_handler(123, 'заявки')
        main_loop_handler(123, 'посмотреть заявки')
        assert mock_send_report.call_count == 3

    @patch('main.remember_user')
    @patch('main.send_report_to_chat')
    @patch('main.send_msg')
    @patch('main.get_main_keyboard_for_user')
    @patch('main.is_admin')
    @patch('main.user_states.get_state')
    def test_report_command_non_admin(self, mock_get_state, mock_is_admin, mock_get_kb, mock_send_msg, mock_send_report, mock_remember_user):
        from main import main_loop_handler
        mock_get_state.return_value = None
        mock_is_admin.return_value = False
        mock_get_kb.return_value = 'user_kb'

    @patch('main.remember_user')
    @patch('main.send_known_users_to_admin')
    @patch('main.user_states.get_state')
    def test_users_list_command(self, mock_get_state, mock_send_users, mock_remember_user):
        from main import main_loop_handler
        mock_get_state.return_value = None
        main_loop_handler(710547454, 'список пользователей')
        mock_send_users.assert_called_once_with(710547454)
        
        main_loop_handler(123, 'отчет')
        mock_send_report.assert_not_called()
        mock_send_msg.assert_called_once_with(123, 'У вас нет доступа к этой команде.', 'user_kb')

    @patch('threading.Thread')
    @patch('main.send_email_report')
    @patch('main.send_msg')
    @patch('main.get_admin_keyboard')
    @patch('main.is_admin')
    @patch('main.user_states.get_state')
    def test_email_command_admin(self, mock_get_state, mock_is_admin, mock_get_admin_kb, mock_send_msg, mock_send_email, mock_thread):
        from main import main_loop_handler
        mock_get_state.return_value = None
        mock_is_admin.return_value = True
        mock_get_admin_kb.return_value = 'admin_kb'
        
        main_loop_handler(123, 'почта')
        mock_thread.assert_called_once_with(target=mock_send_email, daemon=True)
        mock_thread.return_value.start.assert_called_once()
        mock_send_msg.assert_called_once_with(123, 'Отчет отправляется на почту. Ожидайте.', 'admin_kb')

    @patch('main.send_msg')
    @patch('main.get_main_keyboard_for_user')
    @patch('main.is_admin')
    @patch('main.user_states.get_state')
    def test_email_command_non_admin(self, mock_get_state, mock_is_admin, mock_get_kb, mock_send_msg):
        from main import main_loop_handler
        mock_get_state.return_value = None
        mock_is_admin.return_value = False
        mock_get_kb.return_value = 'user_kb'
        
        main_loop_handler(123, 'почта')
        mock_send_msg.assert_called_once_with(123, 'У вас нет доступа к этой команде.', 'user_kb')

    @patch('main.send_msg')
    @patch('main.get_admin_keyboard')
    @patch('main.get_main_keyboard_for_user')
    @patch('main.is_admin')
    @patch('main.user_states.get_state')
    def test_admin_panel_command(self, mock_get_state, mock_is_admin, mock_get_kb, mock_get_admin_kb, mock_send_msg):
        from main import main_loop_handler
        mock_get_state.return_value = None
        
        mock_is_admin.return_value = True
        mock_get_admin_kb.return_value = 'admin_kb'
        main_loop_handler(123, 'админ')
        mock_send_msg.assert_called_once_with(123, 'Панель администратора:', 'admin_kb')
        
        mock_send_msg.reset_mock()
        mock_is_admin.return_value = False
        mock_get_kb.return_value = 'user_kb'
        main_loop_handler(123, 'админ')
        mock_send_msg.assert_called_once_with(123, 'У вас нет доступа к админ-панели.', 'user_kb')

    @patch('main.send_msg')
    @patch('main.get_main_keyboard_for_user')
    @patch('main.user_states.get_state')
    def test_back_command(self, mock_get_state, mock_get_kb, mock_send_msg):
        from main import main_loop_handler
        mock_get_state.return_value = None
        mock_get_kb.return_value = 'main_kb'
        
        main_loop_handler(123, 'назад')
        mock_send_msg.assert_called_once_with(123, 'Главное меню:', 'main_kb')

    @patch('main.send_msg')
    @patch('main.get_main_keyboard_for_user')
    @patch('main.is_admin')
    @patch('main.user_states.get_state')
    def test_help_command_admin(self, mock_get_state, mock_is_admin, mock_get_kb, mock_send_msg):
        from main import main_loop_handler
        mock_get_state.return_value = None
        mock_is_admin.return_value = True
        mock_get_kb.return_value = 'admin_kb'
        
        main_loop_handler(123, 'помощь')
        help_text = (
            "Доступные команды:\n\n"
            "Оставить заявку - подать заявку\n"
            "Посмотреть заявки - показать последние 10 заявок\n"
            "Отчет на почту - отправить отчет на email\n"
            "Помощь - это сообщение"
        )
        mock_send_msg.assert_called_once_with(123, help_text, 'admin_kb')

    @patch('main.send_msg')
    @patch('main.get_main_keyboard_for_user')
    @patch('main.is_admin')
    @patch('main.user_states.get_state')
    def test_help_command_user(self, mock_get_state, mock_is_admin, mock_get_kb, mock_send_msg):
        from main import main_loop_handler
        mock_get_state.return_value = None
        mock_is_admin.return_value = False
        mock_get_kb.return_value = 'user_kb'
        
        main_loop_handler(123, 'помощь')
        help_text = (
            "Доступные команды:\n\n"
            "Оставить заявку - подать заявку\n"
            "Помощь - это сообщение"
        )
        mock_send_msg.assert_called_once_with(123, help_text, 'user_kb')

    @patch('main.send_msg')
    @patch('main.get_main_keyboard_for_user')
    @patch('main.user_states.get_state')
    def test_unknown_command(self, mock_get_state, mock_get_kb, mock_send_msg):
        from main import main_loop_handler
        mock_get_state.return_value = None
        mock_get_kb.return_value = 'main_kb'
        
        main_loop_handler(123, 'что-то непонятное')
        mock_send_msg.assert_called_once_with(123, 'Неизвестная команда. Напишите \'Помощь\' или используйте кнопки.', 'main_kb')


def main_loop_handler(user_id, msg):
    from main import handle_application, handle_message
    if user_states.get_state(user_id):
        handle_application(user_id, msg)
    else:
        handle_message(user_id, msg)


def handle_message(user_id, msg):
    from main import (
        send_msg, get_main_keyboard_for_user, is_admin, handle_application,
        send_report_to_chat, send_email_report, get_admin_keyboard, threading
    )
    
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
                "Посмотреть заявки - показать последние 10 заявок\n"
                "Отчет на почту - отправить отчет на email\n"
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


user_states = None
