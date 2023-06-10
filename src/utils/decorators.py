from pathlib import Path
from os import PathLike, environ
from functools import wraps

from src import shared  # pylint: disable=no-name-in-module


def replaced_by_path(override: PathLike):  # Decorator builder
    """Replace the method's returned path with the override
    if the override exists on disk"""

    def decorator(original_function):  # Built decorator (closure)
        @wraps(original_function)
        def wrapper(*args, **kwargs):  # func's override
            path = Path(override).expanduser()
            if path.exists():
                return path
            return original_function(*args, **kwargs)

        return wrapper

    return decorator


def replaced_by_schema_key(original_method):  # Built decorator (closure)
    """
    Replace the original method's value by the path pointed at in the schema
    by the class' location key (if that override exists)
    """

    @wraps(original_method)
    def wrapper(*args, **kwargs):  # func's override
        source = args[0]
        override = shared.schema.get_string(source.location_key)
        return replaced_by_path(override)(original_method)(*args, **kwargs)

    return wrapper
