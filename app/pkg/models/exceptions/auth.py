from app.pkg.models.base import BaseException

__all__ = [
    "IncorrectLengthFingerprint",
    "IncorrectLengthOTP",
    "IncorrectUsernameOrPassword",
    "TokenExpired"
]


class IncorrectLengthFingerprint(BaseException):
    status_code = 400
    message = "Incorrect fingerprint"


class IncorrectLengthOTP(BaseException):
    status_code = 400
    message = "Incorrect OTP"


class IncorrectUsernameOrPassword(BaseException):
    status_code = 406
    message = "Incorrect username or password or secret key"


class TokenExpired(BaseException):
    status_code = 419
    message = "Session timed out. Try to auth again"
