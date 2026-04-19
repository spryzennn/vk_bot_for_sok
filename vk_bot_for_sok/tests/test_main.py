import pytest
import sys
import os
from unittest.mock import patch, MagicMock, call

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

os.environ['ADMIN_ID'] = '123456789'


@pytest.fixture(autouse=True)
def reset_globals():
    from main import user_states, applications, known_users
    user_states.states.clear()
    user_states.data.clear()
    applications.clear()
    known_users.clear()
    yield
    user_states.states.clear()
    user_states.data.clear()
    applications.clear()
    known_users.clear()


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

    @patch('main.get_admin_ids')
    def test_is_admin_no_admin_id(self, mock_get_admin_ids):
        from main import is_admin
        mock_get_admin_ids.return_value = []
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
        params = call_args[0][1]
        assert params['user_id'] == 123
        assert params['message'] == "Hello"
        assert params['random_id'] == 0

    @patch('main.vk_session')
    def test_send_msg_with_keyboard(self, mock_vk_session):
        from main import send_msg
        mock_method = MagicMock()
        mock_vk_session.method = mock_method
        send_msg(123, "Hello", '{"keyboard": "test"}')
        call_args = mock_method.call_args
        params = call_args[0][1]
        assert params['keyboard'] == '{"keyboard": "test"}'

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

    # --- format_admin_list_text and format_email_list_text ---
    def test_format_admin_list_text_empty(self):
        with patch('main.get_admin_ids', return_value=[]), \
             patch('main.remember_user') as mock_remember:
            from main import format_admin_list_text
            result = format_admin_list_text()
            assert result == "Список админов пуст."
            mock_remember.assert_not_called()

    def test_format_admin_list_text_with_admins(self):
        with patch('main.get_admin_ids', return_value=['123', '456']), \
             patch('main.remember_user', side_effect=lambda aid: f"Admin {aid}"):
            from main import format_admin_list_text
            result = format_admin_list_text()
            expected = "Список пользователей:\n- Admin 123 — ID: 123\n- Admin 456 — ID: 456"
            assert result == expected

    def test_format_email_list_text_empty(self):
        with patch('main.get_notification_emails', return_value=[]):
            from main import format_email_list_text
            result = format_email_list_text()
            assert result == "Список почт пуст."

    def test_format_email_list_text_with_emails(self):
        with patch('main.get_notification_emails', return_value=['a@example.com', 'b@test.org']):
            from main import format_email_list_text
            result = format_email_list_text()
            expected = "Список почт:\n- a@example.com\n- b@test.org"
            assert result == expected

    # --- send_email_list_to_admin ---
    @patch('main.send_msg')
    @patch('main.get_main_keyboard_for_user')
    @patch('main.is_admin')
    def test_send_email_list_to_admin_non_admin(self, mock_is_admin, mock_get_kb, mock_send_msg):
        from main import send_email_list_to_admin
        mock_is_admin.return_value = False
        mock_get_kb.return_value = 'user_kb'
        send_email_list_to_admin(123)
        mock_send_msg.assert_called_once_with(123, "У вас нет доступа к этой команде.", 'user_kb')

    @patch('main.get_admin_keyboard')
    @patch('main.send_msg')
    @patch('main.format_email_list_text')
    @patch('main.is_admin')
    def test_send_email_list_to_admin_admin(self, mock_is_admin, mock_format, mock_send_msg, mock_get_admin_kb):
        from main import send_email_list_to_admin
        mock_is_admin.return_value = True
        mock_format.return_value = "Email list text"
        mock_get_admin_kb.return_value = 'admin_kb'
        send_email_list_to_admin(123)
        mock_send_msg.assert_called_once_with(123, "Email list text", 'admin_kb')

    # --- send_known_users_to_admin (admin branch) ---
    @patch('main.get_admin_keyboard')
    @patch('main.send_msg')
    @patch('main.format_admin_list_text')
    @patch('main.is_admin')
    def test_send_known_users_to_admin_admin(self, mock_is_admin, mock_format, mock_send_msg, mock_get_admin_kb):
        from main import send_known_users_to_admin
        mock_is_admin.return_value = True
        mock_format.return_value = "Admin list text"
        mock_get_admin_kb.return_value = 'admin_kb'
        send_known_users_to_admin(123)
        mock_send_msg.assert_called_once_with(123, "Admin list text", 'admin_kb')

    # --- remember_user exception handling ---
    @patch('main.vk_session')
    @patch('main.logger')
    def test_remember_user_exception(self, mock_logger, mock_vk_session):
        from main import remember_user
        from main import known_users
        known_users.clear()
        mock_vk_session.method.side_effect = Exception("API error")
        user_id = 123
        result = remember_user(user_id)
        assert result == f"Пользователь {user_id}"
        assert known_users[user_id] == f"Пользователь {user_id}"
        mock_logger.error.assert_called_once()


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

    @patch('main.get_admin_ids')
    @patch('main.logger')
    @patch('main.send_msg')
    @patch('main.get_main_keyboard_for_user')
    @patch('main.get_application_keyboard_with_skip')
    @patch('main.send_new_application_email')
    def test_handle_application_waiting_note_with_note(self, mock_email, mock_kb, mock_main_kb, mock_send_msg, mock_logger, mock_get_admin_ids):
        from main import handle_application
        from main import applications
        from main import user_states
        applications.clear()
        mock_get_admin_ids.return_value = ['123456789']
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

    @patch('main.get_admin_ids')
    @patch('main.send_msg')
    @patch('main.get_main_keyboard_for_user')
    def test_notify_admin_about_application(self, mock_main_kb, mock_send_msg, mock_get_admin_ids):
        from main import notify_admin_about_application
        mock_get_admin_ids.return_value = ['710547454']
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

    @patch('main.remember_user')
    @patch('main.get_admin_ids')
    @patch('main.is_admin')
    @patch('main.send_msg')
    @patch('main.get_admin_keyboard')
    def test_send_known_users_to_admin(self, mock_get_admin_kb, mock_send_msg, mock_is_admin, mock_get_admin_ids, mock_remember_user):
        from main import send_known_users_to_admin
        mock_is_admin.return_value = True
        mock_get_admin_kb.return_value = 'admin_kb'
        mock_get_admin_ids.return_value = ['710547454', '540047989']
        mock_remember_user.side_effect = lambda aid: f"User {aid}"
        send_known_users_to_admin(710547454)
        expected = "Список пользователей:\n- User 710547454 — ID: 710547454\n- User 540047989 — ID: 540047989"
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

    @patch('main.admin_id', '123')
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

    @patch('main.admin_id', '123')
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

    @patch('main.admin_id', '123')
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

    @patch('main.send_known_users_to_admin')
    @patch('main.user_states.get_state')
    def test_users_list_command_admin(self, mock_get_state, mock_send_users):
        from main import main_loop_handler
        mock_get_state.return_value = None
        main_loop_handler(710547454, 'список пользователей')
        mock_send_users.assert_called_once_with(710547454)

    @patch('main.is_admin')
    @patch('main.send_msg')
    @patch('main.get_main_keyboard_for_user')
    @patch('main.user_states.get_state')
    def test_users_list_command_non_admin(self, mock_get_state, mock_get_kb, mock_send_msg, mock_is_admin):
        from main import main_loop_handler
        mock_get_state.return_value = None
        mock_is_admin.return_value = False
        mock_get_kb.return_value = 'user_kb'
        
        main_loop_handler(123, 'список пользователей')
        mock_send_msg.assert_called_once_with(123, 'У вас нет доступа к этой команде.', 'user_kb')

    @patch('threading.Thread')
    @patch('main.send_msg')
    @patch('main.get_admin_keyboard')
    @patch('main.remember_user')
    @patch('main.add_admin_id')
    @patch('main.user_states.get_state')
    def test_waiting_admin_id_success(self, mock_get_state, mock_add_admin, mock_remember, mock_get_admin_kb, mock_send_msg):
        from main import main_loop_handler
        mock_get_state.return_value = "waiting_admin_id"
        mock_add_admin.return_value = True
        mock_remember.return_value = "New Admin"
        mock_get_admin_kb.return_value = 'admin_kb'

        main_loop_handler(123, "999999")

        mock_add_admin.assert_called_once_with(999999)
        mock_remember.assert_called_once_with(999999)
        mock_send_msg.assert_called_once_with(123, "Админ New Admin добавлен.", 'admin_kb')

    @patch('main.send_msg')
    @patch('main.get_admin_keyboard')
    @patch('main.remember_user')
    @patch('main.add_admin_id')
    @patch('main.user_states.get_state')
    def test_waiting_admin_id_duplicate(self, mock_get_state, mock_add_admin, mock_remember, mock_get_admin_kb, mock_send_msg):
        from main import main_loop_handler
        mock_get_state.return_value = "waiting_admin_id"
        mock_add_admin.return_value = False  # already exists
        mock_remember.return_value = "Existing Admin"
        mock_get_admin_kb.return_value = 'admin_kb'

        main_loop_handler(123, "999999")

        mock_send_msg.assert_called_once_with(123, "Existing Admin уже есть в списке админов.", 'admin_kb')

    @patch('main.send_msg')
    @patch('main.get_admin_input_keyboard')
    @patch('main.user_states.get_state')
    def test_waiting_admin_id_invalid_input(self, mock_get_state, mock_get_input_kb, mock_send_msg):
        from main import main_loop_handler
        mock_get_state.return_value = "waiting_admin_id"
        mock_get_input_kb.return_value = 'input_kb'

        main_loop_handler(123, "не число")

        mock_send_msg.assert_called_once_with(123, "Введите ID пользователя или 'Отмена':", 'input_kb')

    @patch('main.send_msg')
    @patch('main.get_admin_keyboard')
    @patch('main.user_states.get_state')
    def test_waiting_admin_id_cancel(self, mock_get_state, mock_get_admin_kb, mock_send_msg):
        from main import main_loop_handler
        mock_get_state.return_value = "waiting_admin_id"
        mock_get_admin_kb.return_value = 'admin_kb'

        main_loop_handler(123, "отмена")

        mock_send_msg.assert_called_once_with(123, "Отменено.", 'admin_kb')

    # --- waiting_remove_admin_id ---
    @patch('main.send_msg')
    @patch('main.get_admin_keyboard')
    @patch('main.remember_user')
    @patch('main.remove_admin_id')
    @patch('main.user_states.get_state')
    def test_waiting_remove_admin_id_success(self, mock_get_state, mock_remove_admin, mock_remember, mock_get_admin_kb, mock_send_msg):
        from main import main_loop_handler
        mock_get_state.return_value = "waiting_remove_admin_id"
        mock_remove_admin.return_value = True
        mock_remember.return_value = "Admin To Remove"
        mock_get_admin_kb.return_value = 'admin_kb'

        main_loop_handler(123, "999999")

        mock_remove_admin.assert_called_once_with(999999)
        mock_send_msg.assert_called_once_with(123, "Админ Admin To Remove удалён.", 'admin_kb')

    @patch('main.send_msg')
    @patch('main.get_admin_keyboard')
    @patch('main.remember_user')
    @patch('main.remove_admin_id')
    @patch('main.user_states.get_state')
    def test_waiting_remove_admin_id_not_found(self, mock_get_state, mock_remove_admin, mock_remember, mock_get_admin_kb, mock_send_msg):
        from main import main_loop_handler
        mock_get_state.return_value = "waiting_remove_admin_id"
        mock_remove_admin.return_value = False
        mock_remember.return_value = "Nonexistent"
        mock_get_admin_kb.return_value = 'admin_kb'

        main_loop_handler(123, "999999")

        mock_send_msg.assert_called_once_with(123, "Nonexistent не находится в списке админов.", 'admin_kb')

    @patch('main.send_msg')
    @patch('main.get_admin_keyboard')
    @patch('main.user_states.get_state')
    def test_waiting_remove_admin_id_try_remove_main_admin(self, mock_get_state, mock_get_admin_kb, mock_send_msg):
        from main import main_loop_handler, admin_id
        mock_get_state.return_value = "waiting_remove_admin_id"
        mock_get_admin_kb.return_value = 'admin_kb'

        main_loop_handler(123, str(admin_id))

        mock_send_msg.assert_called_once_with(123, "Невозможно удалить главного админа.", 'admin_kb')

    @patch('main.send_msg')
    @patch('main.get_admin_input_keyboard')
    @patch('main.user_states.get_state')
    def test_waiting_remove_admin_id_invalid_input(self, mock_get_state, mock_get_input_kb, mock_send_msg):
        from main import main_loop_handler
        mock_get_state.return_value = "waiting_remove_admin_id"
        mock_get_input_kb.return_value = 'input_kb'

        main_loop_handler(123, "abc")

        mock_send_msg.assert_called_once_with(123, "Введите ID пользователя или 'Отмена':", 'input_kb')

    @patch('main.send_msg')
    @patch('main.get_admin_keyboard')
    @patch('main.user_states.get_state')
    def test_waiting_remove_admin_id_cancel(self, mock_get_state, mock_get_admin_kb, mock_send_msg):
        from main import main_loop_handler
        mock_get_state.return_value = "waiting_remove_admin_id"
        mock_get_admin_kb.return_value = 'admin_kb'

        main_loop_handler(123, "отмена")

        mock_send_msg.assert_called_once_with(123, "Отменено.", 'admin_kb')

    # --- waiting_email ---
    @patch('main.send_msg')
    @patch('main.get_admin_keyboard')
    @patch('main.add_notification_email')
    @patch('main.user_states.get_state')
    def test_waiting_email_add_success(self, mock_get_state, mock_add_email, mock_get_admin_kb, mock_send_msg):
        from main import main_loop_handler
        mock_get_state.return_value = "waiting_email"
        mock_add_email.return_value = True
        mock_get_admin_kb.return_value = 'admin_kb'

        main_loop_handler(123, "new@example.com")

        mock_add_email.assert_called_once_with("new@example.com")
        mock_send_msg.assert_called_once_with(123, "Почта new@example.com добавлена.", 'admin_kb')

    @patch('main.send_msg')
    @patch('main.get_admin_keyboard')
    @patch('main.add_notification_email')
    @patch('main.user_states.get_state')
    def test_waiting_email_duplicate(self, mock_get_state, mock_add_email, mock_get_admin_kb, mock_send_msg):
        from main import main_loop_handler
        mock_get_state.return_value = "waiting_email"
        mock_add_email.return_value = False
        mock_get_admin_kb.return_value = 'admin_kb'

        main_loop_handler(123, "existing@example.com")

        mock_send_msg.assert_called_once_with(123, "Эта почта уже есть в списке.", 'admin_kb')

    @patch('main.send_msg')
    @patch('main.get_admin_input_keyboard')
    @patch('main.user_states.get_state')
    def test_waiting_email_invalid_format(self, mock_get_state, mock_get_input_kb, mock_send_msg):
        from main import main_loop_handler
        mock_get_state.return_value = "waiting_email"
        mock_get_input_kb.return_value = 'input_kb'

        main_loop_handler(123, "invalid-email")

        mock_send_msg.assert_called_once_with(123, "Введите корректный email или 'Отмена':", 'input_kb')

    @patch('main.send_msg')
    @patch('main.get_admin_keyboard')
    @patch('main.user_states.get_state')
    def test_waiting_email_cancel(self, mock_get_state, mock_get_admin_kb, mock_send_msg):
        from main import main_loop_handler
        mock_get_state.return_value = "waiting_email"
        mock_get_admin_kb.return_value = 'admin_kb'

        main_loop_handler(123, "отмена")

        mock_send_msg.assert_called_once_with(123, "Отменено.", 'admin_kb')

    # --- waiting_remove_email ---
    @patch('main.send_msg')
    @patch('main.get_admin_keyboard')
    @patch('main.remove_notification_email')
    @patch('main.user_states.get_state')
    def test_waiting_remove_email_success(self, mock_get_state, mock_remove_email, mock_get_admin_kb, mock_send_msg):
        from main import main_loop_handler
        mock_get_state.return_value = "waiting_remove_email"
        mock_remove_email.return_value = True
        mock_get_admin_kb.return_value = 'admin_kb'

        main_loop_handler(123, "remove@example.com")

        mock_remove_email.assert_called_once_with("remove@example.com")
        mock_send_msg.assert_called_once_with(123, "Почта remove@example.com удалена.", 'admin_kb')

    @patch('main.send_msg')
    @patch('main.get_admin_keyboard')
    @patch('main.remove_notification_email')
    @patch('main.user_states.get_state')
    def test_waiting_remove_email_not_found(self, mock_get_state, mock_remove_email, mock_get_admin_kb, mock_send_msg):
        from main import main_loop_handler
        mock_get_state.return_value = "waiting_remove_email"
        mock_remove_email.return_value = False
        mock_get_admin_kb.return_value = 'admin_kb'

        main_loop_handler(123, "nonexistent@example.com")

        mock_send_msg.assert_called_once_with(123, "Этой почты нет в списке.", 'admin_kb')

    @patch('main.send_msg')
    @patch('main.get_admin_keyboard')
    @patch('main.user_states.get_state')
    def test_waiting_remove_email_cancel(self, mock_get_state, mock_get_admin_kb, mock_send_msg):
        from main import main_loop_handler
        mock_get_state.return_value = "waiting_remove_email"
        mock_get_admin_kb.return_value = 'admin_kb'

        main_loop_handler(123, "отмена")

        mock_send_msg.assert_called_once_with(123, "Отменено.", 'admin_kb')


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
        
        main_loop_handler(123, 'отчет')
        mock_send_msg.assert_called_once_with(123, 'У вас нет доступа к этой команде.', 'user_kb')

    @patch('main.remember_user')
    @patch('main.send_known_users_to_admin')
    @patch('main.user_states.get_state')
    def test_users_list_command_admin(self, mock_get_state, mock_send_users, mock_remember_user):
        from main import main_loop_handler
        mock_get_state.return_value = None
        main_loop_handler(710547454, 'список пользователей')
        mock_send_users.assert_called_once_with(710547454)

    @patch('main.is_admin')
    @patch('main.send_msg')
    @patch('main.get_main_keyboard_for_user')
    @patch('main.user_states.get_state')
    def test_users_list_command_non_admin(self, mock_get_state, mock_get_kb, mock_send_msg, mock_is_admin):
        from main import main_loop_handler
        mock_get_state.return_value = None
        mock_is_admin.return_value = False
        mock_get_kb.return_value = 'user_kb'
        
        main_loop_handler(123, 'список пользователей')
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

