from __future__ import annotations

import time
from datetime import date, datetime
from typing import Any, Dict, List, Tuple, TypeVar

import pydantic

from app.pkg.models import types

__all__ = ["BaseModel", "Model"]

Model = TypeVar("Model", bound="BaseModel")


class BaseModel(pydantic.BaseModel):
    def __cast_value(self, v, show_secrets, **kwargs):
        if isinstance(v, List) or isinstance(v, Tuple):
            return [
                self.__cast_value(v=ve, show_secrets=show_secrets, **kwargs) for ve in v
            ]
        elif isinstance(v, pydantic.SecretBytes):
            return v.get_secret_value().decode() if show_secrets else str(v)
        elif isinstance(v, pydantic.SecretStr):
            return v.get_secret_value() if show_secrets else str(v)
        elif isinstance(v, Dict) and v:
            return self.to_dict(show_secrets=show_secrets, values=v, **kwargs)

        return v

    def to_dict(
        self, show_secrets: bool = False, values: Dict[Any, Any] = None, **kwargs
    ) -> Dict[Any, Any]:
        """Make transfer model to Dict object.

        Args:
            show_secrets: bool. default False. Shows secret in dict object if True.
            values: Using an object to write to a Dict object.
        Keyword Args:
            Optional arguments to be passed to the Dict object.

        Returns: Dict object with reveal password filed.
        """
        values = self.dict(**kwargs).items() if not values else values.items()
        r = {}
        for k, v in values:
            if isinstance(v, pydantic.SecretBytes):
                v = v.get_secret_value().decode() if show_secrets else str(v)
            elif isinstance(v, pydantic.SecretStr):
                v = v.get_secret_value() if show_secrets else str(v)
            elif isinstance(v, Dict):
                v = self.to_dict(show_secrets=show_secrets, values=v)
            r[k] = v
        return r

    def delete_attribute(self, attr: str) -> BaseModel:
        """Delete `attr` field from model.

        Args:
            attr: str value, implements name of field.
        Returns: self object.
        """
        delattr(self, attr)
        return self

    class Config:
        use_enum_values = True
        json_encoders = {
            pydantic.SecretStr: lambda v: v.get_secret_value() if v else None,
            pydantic.SecretBytes: lambda v: v.get_secret_value() if v else None,
            types.EncryptedSecretBytes: lambda v: v.get_secret_value() if v else None,
            bytes: lambda v: v.decode() if v else None,
            datetime: lambda v: int(v.timestamp()) if v else None,
            date: lambda v: int(time.mktime(v.timetuple())) if v else None,
        }
        allow_population_by_field_name = True
