import datetime

from pydantic import PositiveInt

from app.pkg.models.base import BaseModel

__all__ = [
    "JWTToken",
    "CreateJWTTokenCommand",
    "ReadJWTTokenQuery",
    "ReadJWTTokenQueryByFingerprint",
    "UpdateJWTTokenCommand",
    "DeleteJWTTokenCommand",
]

from app.pkg.models.types import NotEmptySecretStr


class BaseJWTToken(BaseModel):
    """Base class for refresh token."""


class JWTToken(BaseJWTToken):
    """RefreshToken from database."""
    id: PositiveInt
    user_id: PositiveInt
    refresh_token: NotEmptySecretStr
    fingerprint: NotEmptySecretStr
    expiresat: float = 30*24*60*60  # month in seconds


# Commands
class CreateJWTTokenCommand(BaseJWTToken):
    user_id: PositiveInt
    refresh_token: NotEmptySecretStr
    fingerprint: NotEmptySecretStr
    expiresat: float = 30*24*60*60


class UpdateJWTTokenCommand(BaseJWTToken):
    user_id: PositiveInt
    refresh_token: NotEmptySecretStr
    fingerprint: NotEmptySecretStr
    expiresat: float = 30*24*60*60


class DeleteJWTTokenCommand(BaseJWTToken):
    user_id: PositiveInt
    fingerprint: NotEmptySecretStr
    refresh_token: NotEmptySecretStr


# Queries
class ReadJWTTokenQuery(BaseJWTToken):
    user_id: PositiveInt
    refresh_token: NotEmptySecretStr


class ReadJWTTokenQueryByFingerprint(BaseJWTToken):
    user_id: PositiveInt
    fingerprint: NotEmptySecretStr
