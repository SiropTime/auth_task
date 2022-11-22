from pydantic import PositiveInt

from app.pkg.models.base import BaseModel

from app.pkg.models.types import NotEmptySecretStr


class BaseAccessToken(BaseModel):
    """
    Base class for access token
    """


class AccessToken(BaseAccessToken):
    """
    In this case this is universal model because we don't have many rows
    """
    refresh_id: PositiveInt
    access_token: NotEmptySecretStr


