import re

class ValidationError(Exception):
    pass


def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValidationError(f"Invalid email: {email}")
    return email


def is_valid_mobile(number):
    pattern = r'^\+[1-9]\d{1,3}\d{6,14}$'
    if not re.match(pattern, number):
        raise ValidationError(f"Invalid mobile number: {number}")
    return number

def validatePassword(password):
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long.")

    if not re.search(r"[A-Z]", password):
        raise ValidationError("Password must contain at least one uppercase letter.")

    if not re.search(r"[a-z]", password):
        raise ValidationError("Password must contain at least one lowercase letter.")

    if not re.search(r"\d", password):
        raise ValidationError("Password must contain at least one digit.")

    if not re.search(r"[@$!%*?&]", password):
        raise ValidationError("Password must contain at least one special character (@$!%*?&).")

    return password        



def match_password(password,confirm_password):
    if password==confirm_password:
        return password
    raise ValidationError("Error: Password Doesn't match. Please Try Again")

    
