import re

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"^[0-9+\-\s]{7,15}$")


def valid_email(v):
    return bool(v and EMAIL_RE.match(v.strip()))


def valid_phone(v):
    return bool(v and PHONE_RE.match(v.strip()))


def require_fields(data, fields):
    missing = [f for f in fields if not (data.get(f) not in (None, ""))]
    return missing


def seat_label_ok(s):
    # Accept A1..J4 style or numeric 01..40
    if not s:
        return False
    s = str(s).strip().upper()
    if re.match(r"^[A-J][1-4]$", s):
        return True
    if re.match(r"^\d{1,2}$", s) and 1 <= int(s) <= 40:
        return True
    return False
