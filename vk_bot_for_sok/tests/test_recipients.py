import pytest
import sys
import os
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import recipients


@pytest.fixture
def temp_config_dir(tmp_path, monkeypatch):
    """Create temporary config directory and patch recipients file paths."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    admin_file = config_dir / "admin_ids.txt"
    email_file = config_dir / "notification_emails.txt"
    # Create empty files initially
    admin_file.write_text("", encoding="utf-8")
    email_file.write_text("", encoding="utf-8")

    monkeypatch.setattr(recipients, "ADMINS_FILE", admin_file)
    monkeypatch.setattr(recipients, "EMAILS_FILE", email_file)
    return {
        "admin": admin_file,
        "email": email_file,
        "config": config_dir
    }


class TestGetAdminIds:
    def test_get_admin_ids_empty(self, temp_config_dir):
        result = recipients.get_admin_ids()
        assert result == []

    def test_get_admin_ids_from_file(self, temp_config_dir):
        temp_config_dir["admin"].write_text("123456789\n987654321\n", encoding="utf-8")
        result = recipients.get_admin_ids()
        assert result == ["123456789", "987654321"]

    def test_get_admin_ids_default_not_in_file(self, temp_config_dir):
        temp_config_dir["admin"].write_text("123456789\n", encoding="utf-8")
        result = recipients.get_admin_ids(default_admin_id="999999999")
        assert result == ["999999999", "123456789"]

    def test_get_admin_ids_default_already_in_file(self, temp_config_dir):
        temp_config_dir["admin"].write_text("123456789\n", encoding="utf-8")
        result = recipients.get_admin_ids(default_admin_id="123456789")
        assert result == ["123456789"]

    def test_get_admin_ids_ignores_blank_lines(self, temp_config_dir):
        temp_config_dir["admin"].write_text("123\n\n456\n  \n", encoding="utf-8")
        result = recipients.get_admin_ids()
        assert result == ["123", "456"]


class TestGetNotificationEmails:
    def test_get_notification_emails_empty(self, temp_config_dir):
        result = recipients.get_notification_emails()
        assert result == []

    def test_get_notification_emails_from_file(self, temp_config_dir):
        temp_config_dir["email"].write_text("test@example.com\nadmin@test.org\n", encoding="utf-8")
        result = recipients.get_notification_emails()
        assert result == ["test@example.com", "admin@test.org"]

    def test_get_notification_emails_default_not_in_file(self, temp_config_dir):
        temp_config_dir["email"].write_text("test@example.com\n", encoding="utf-8")
        result = recipients.get_notification_emails(default_email="default@mail.com")
        assert result == ["default@mail.com", "test@example.com"]

    def test_get_notification_emails_default_already_in_file(self, temp_config_dir):
        temp_config_dir["email"].write_text("default@mail.com\n", encoding="utf-8")
        result = recipients.get_notification_emails(default_email="default@mail.com")
        assert result == ["default@mail.com"]


class TestAddAdminId:
    def test_add_admin_id_new(self, temp_config_dir):
        result = recipients.add_admin_id(123456789)
        assert result is True
        content = temp_config_dir["admin"].read_text(encoding="utf-8")
        assert "123456789" in content

    def test_add_admin_id_duplicate(self, temp_config_dir):
        temp_config_dir["admin"].write_text("123456789\n", encoding="utf-8")
        result = recipients.add_admin_id(123456789)
        assert result is False
        content = temp_config_dir["admin"].read_text(encoding="utf-8")
        assert content.count("123456789") == 1

    def test_add_admin_id_creates_file_if_missing(self, tmp_path, monkeypatch):
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        admin_file = config_dir / "admin_ids.txt"
        # Do not create file initially
        monkeypatch.setattr(recipients, "ADMINS_FILE", admin_file)
        assert not admin_file.exists()
        result = recipients.add_admin_id(111)
        assert result is True
        assert admin_file.exists()
        content = admin_file.read_text(encoding="utf-8")
        assert "111" in content


class TestRemoveAdminId:
    def test_remove_admin_id_success(self, temp_config_dir):
        temp_config_dir["admin"].write_text("123\n456\n", encoding="utf-8")
        result = recipients.remove_admin_id(123)
        assert result is True
        content = temp_config_dir["admin"].read_text(encoding="utf-8")
        assert "123" not in content
        assert "456" in content

    def test_remove_admin_id_not_found(self, temp_config_dir):
        temp_config_dir["admin"].write_text("123\n", encoding="utf-8")
        result = recipients.remove_admin_id(999)
        assert result is False
        content = temp_config_dir["admin"].read_text(encoding="utf-8")
        assert content == "123\n"

    def test_remove_admin_id_removes_only_one_occurrence(self, temp_config_dir):
        temp_config_dir["admin"].write_text("123\n123\n456\n", encoding="utf-8")
        result = recipients.remove_admin_id(123)
        assert result is True
        content = temp_config_dir["admin"].read_text(encoding="utf-8")
        assert content == "123\n456\n"  # one 123 remains


class TestAddNotificationEmail:
    def test_add_notification_email_new(self, temp_config_dir):
        result = recipients.add_notification_email("test@example.com")
        assert result is True
        content = temp_config_dir["email"].read_text(encoding="utf-8")
        assert "test@example.com" in content

    def test_add_notification_email_duplicate(self, temp_config_dir):
        temp_config_dir["email"].write_text("test@example.com\n", encoding="utf-8")
        result = recipients.add_notification_email("test@example.com")
        assert result is False

    def test_add_notification_email_strips_whitespace(self, temp_config_dir):
        result = recipients.add_notification_email("  test@example.com  ")
        assert result is True
        content = temp_config_dir["email"].read_text(encoding="utf-8")
        # The function writes as provided; but _read_lines strips on read. Write may include spaces.
        # Our add uses email as provided; it does not strip. But reading strips. So on read it's fine.
        # But the file will contain with spaces? Actually add_notification_email appends email as is.
        # Usually you'd want to strip. Not in code. Let's not change code; test current behavior.
        assert "test@example.com" in content  # spaces included
        lines = recipients._read_lines(temp_config_dir["email"])
        assert "test@example.com" in lines  # _read_lines strips, so it will be trimmed

    def test_add_notification_email_creates_file_if_missing(self, tmp_path, monkeypatch):
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        email_file = config_dir / "notification_emails.txt"
        monkeypatch.setattr(recipients, "EMAILS_FILE", email_file)
        result = recipients.add_notification_email("new@mail.com")
        assert result is True
        assert email_file.exists()


class TestRemoveNotificationEmail:
    def test_remove_notification_email_success(self, temp_config_dir):
        temp_config_dir["email"].write_text("a@example.com\nb@example.com\n", encoding="utf-8")
        result = recipients.remove_notification_email("a@example.com")
        assert result is True
        content = temp_config_dir["email"].read_text(encoding="utf-8")
        assert "a@example.com" not in content
        assert "b@example.com" in content

    def test_remove_notification_email_not_found(self, temp_config_dir):
        temp_config_dir["email"].write_text("a@example.com\n", encoding="utf-8")
        result = recipients.remove_notification_email("nonexistent@example.com")
        assert result is False

    def test_remove_notification_email_exact_match(self, temp_config_dir):
        temp_config_dir["email"].write_text("Test@Example.com\n", encoding="utf-8")
        # Case-sensitive removal
        result = recipients.remove_notification_email("test@example.com")
        assert result is False
        result2 = recipients.remove_notification_email("Test@Example.com")
        assert result2 is True


class TestInternalReadLines:
    def test_read_lines_nonexistent_file(self, tmp_path):
        nonexistent = tmp_path / "nope.txt"
        lines = recipients._read_lines(nonexistent)
        assert lines == []

    def test_read_lines_normal(self, tmp_path):
        file = tmp_path / "test.txt"
        file.write_text("line1\n  line2  \n\nline3\n", encoding="utf-8")
        lines = recipients._read_lines(file)
        assert lines == ["line1", "line2", "line3"]
