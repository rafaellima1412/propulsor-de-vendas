import functools
from typing import Any


def _auto_close(method):
    @functools.wraps(method)
    def wrapper(self, *args: Any, **kwargs: Any):
        try:
            return method(self, *args, **kwargs)
        finally:
            self.db.close()

    return wrapper


class BaseRepository:
    db: Any

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        for name, attr in list(vars(cls).items()):
            if name.startswith("_") or not callable(attr):
                continue
            setattr(cls, name, _auto_close(attr))