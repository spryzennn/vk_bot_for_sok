import pytest
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

os.environ['ADMIN_ID'] = '710547454'

class TestKeyboards:
    def test_get_main_keyboard(self):
        from keyboards import get_main_keyboard
        result = get_main_keyboard()
        
        # Should be valid JSON
        keyboard = json.loads(result)
        
        # Check structure
        assert keyboard['one_time'] is False
        assert len(keyboard['buttons']) == 3
        assert keyboard['buttons'][0][0]['action']['label'] == 'Оставить заявку'
        assert keyboard['buttons'][1][0]['action']['label'] == 'Панель админа'
        assert keyboard['buttons'][2][0]['action']['label'] == 'Помощь'

    def test_get_main_keyboard_admin(self):
        from keyboards import get_main_keyboard_admin
        result = get_main_keyboard_admin()
        
        keyboard = json.loads(result)
        
        assert keyboard['one_time'] is False
        assert len(keyboard['buttons']) == 3
        assert keyboard['buttons'][0][0]['action']['label'] == 'Оставить заявку'
        assert keyboard['buttons'][1][0]['action']['label'] == 'Панель админа'
        assert keyboard['buttons'][2][0]['action']['label'] == 'Помощь'

    def test_get_application_keyboard(self):
        from keyboards import get_application_keyboard
        result = get_application_keyboard()
        
        keyboard = json.loads(result)
        
        assert keyboard['one_time'] is True
        assert len(keyboard['buttons']) == 1
        assert keyboard['buttons'][0][0]['action']['label'] == 'Отмена'
        assert keyboard['buttons'][0][0]['color'] == 'negative'

    def test_get_application_keyboard_with_skip(self):
        from keyboards import get_application_keyboard_with_skip
        result = get_application_keyboard_with_skip()
        
        keyboard = json.loads(result)
        
        assert keyboard['one_time'] is True
        assert len(keyboard['buttons']) == 2
        assert keyboard['buttons'][0][0]['action']['label'] == 'Пропустить'
        assert keyboard['buttons'][1][0]['action']['label'] == 'Отмена'

    def test_get_cancel_keyboard(self):
        from keyboards import get_cancel_keyboard
        result = get_cancel_keyboard()
        
        keyboard = json.loads(result)
        
        assert keyboard['one_time'] is True
        assert len(keyboard['buttons']) == 1
        assert keyboard['buttons'][0][0]['action']['label'] == 'Отмена'
        assert keyboard['buttons'][0][0]['color'] == 'negative'

    def test_get_empty_keyboard(self):
        from keyboards import get_empty_keyboard
        result = get_empty_keyboard()
        
        keyboard = json.loads(result)
        
        assert keyboard == {"buttons": []}

    def test_get_admin_keyboard(self):
        from keyboards import get_admin_keyboard
        result = get_admin_keyboard()
        
        keyboard = json.loads(result)
        
        assert keyboard['one_time'] is False
        assert len(keyboard['buttons']) == 2
        assert keyboard['buttons'][0][0]['action']['label'] == 'Список пользователей'
        assert keyboard['buttons'][1][0]['action']['label'] == 'Назад'
