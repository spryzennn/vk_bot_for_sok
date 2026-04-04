from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
ADMINS_FILE = BASE_DIR / "config" / "admin_ids.txt"
EMAILS_FILE = BASE_DIR / "config" / "notification_emails.txt"


def _read_lines(file_path):
    if not file_path.exists():
        return []
    return [line.strip() for line in file_path.read_text(encoding="utf-8").splitlines() if line.strip()]


def get_admin_ids(default_admin_id=None):
    admin_ids = _read_lines(ADMINS_FILE)
    if default_admin_id and str(default_admin_id) not in admin_ids:
        admin_ids.insert(0, str(default_admin_id))
    return admin_ids


def get_notification_emails(default_email=None):
    emails = _read_lines(EMAILS_FILE)
    if default_email and default_email not in emails:
        emails.insert(0, default_email)
    return emails
