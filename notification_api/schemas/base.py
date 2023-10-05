import uuid
from typing import Any

import orjson
from pydantic import BaseModel


def orjson_dumps(val: Any, *, default: Any) -> str:
    """Дамп в JSON.

    Parameters:
        val: Значение.
        default: Значение по умолчанию.

    Returns:
        str: json строка.
    """
    return orjson.dumps(val, default=default).decode()


class Model(BaseModel):
    """Модель с более быстрым сериализатором orjson."""

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
        validate_assignment = True

        json_encoders = {
            uuid.UUID: lambda u: str(u),
        }
