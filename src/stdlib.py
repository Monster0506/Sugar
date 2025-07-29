import datetime
import os
import time
from math import (
    acos,
    asin,
    atan,
    ceil,
    cos,
    degrees,
    e,
    exp,
    factorial,
    floor,
    gcd,
    lcm,
    log,
    log10,
    pi,
    radians,
    sin,
    sqrt,
    tan,
)
from random import choice, randint, random, sample, shuffle

from src.ast_nodes import StdLibCall


DEFAULT_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"  # YYYY-MM-DDTHH:MM:SS.microseconds

library = {
    "Math": {
        "PI": StdLibCall(lambda: pi),
        "SQRT": StdLibCall(lambda x: sqrt(x)),
        "E": StdLibCall(lambda: e),
        "FLOOR": StdLibCall(lambda x: floor(x)),
        "CEIL": StdLibCall(lambda x: ceil(x)),
        "ROUND": StdLibCall(lambda x: round(x)),
        "POW": StdLibCall(lambda x, y: pow(x, y)),
        "ABS": StdLibCall(lambda x: abs(x)),
        "MIN": StdLibCall(lambda *x: min(*x)),
        "MAX": StdLibCall(lambda *x: max(*x)),
        "SIN": StdLibCall(lambda x: sin(x)),
        "COS": StdLibCall(lambda x: cos(x)),
        "TAN": StdLibCall(lambda x: tan(x)),
        "ASIN": StdLibCall(lambda x: asin(x)),
        "ACOS": StdLibCall(lambda x: acos(x)),
        "ATAN": StdLibCall(lambda x: atan(x)),
        "LOG": StdLibCall(lambda x, y: log(x, y)),
        "LOG10": StdLibCall(lambda x: log10(x)),
        "EXP": StdLibCall(lambda x: exp(x)),
        "FACTORIAL": StdLibCall(lambda x: factorial(x)),
        "GCD": StdLibCall(lambda *args: gcd(*args)),
        "LCM": StdLibCall(lambda *args: lcm(*args)),
        "DEGREES": StdLibCall(lambda x: degrees(x)),
        "RADIANS": StdLibCall(lambda x: radians(x)),
    },
    "Random": {
        "INT": StdLibCall(lambda x, y: randint(x, y)),
        "FLOAT": StdLibCall(lambda: random()),
        "CHOICE": StdLibCall(lambda x: choice(x)),
        "SHUFFLE": StdLibCall(lambda x: _shuffle(x)),
        "SAMPLE": StdLibCall(lambda x, k: sample(x, k)),
    },
    "Time": {
        "NOW_STR": StdLibCall(lambda: _get_current_time_str()),
        "NOW_MAP": StdLibCall(lambda: _get_time_components_now()),
        "TIMESTAMP": StdLibCall(lambda: _get_current_timestamp()),
        "FORMAT_STR": StdLibCall(lambda ts, cf, tf: _format_time_str(ts, cf, tf)),
        "PARSE_TO_MAP": StdLibCall(lambda ts, f: _parse_time_to_map(ts, f)),
        "SLEEP": StdLibCall(lambda seconds: time.sleep(seconds)),
        "DEFAULT_FORMAT": StdLibCall(lambda: DEFAULT_DATETIME_FORMAT),
    },
    "IO": {
        "PRINT": StdLibCall(lambda *args: print(*args)),
        "INPUT": StdLibCall(lambda args: input(args)),
    },
    "System": {
        "EXIT": StdLibCall(lambda args: exit(args)),
    },
    "File": {
        "READ": StdLibCall(
            lambda filepath, encoding="utf-8": _file_read(filepath, encoding)
        ),
        "WRITE": StdLibCall(
            lambda filepath, content, append=False, encoding="utf-8": _file_write(
                filepath, content, append, encoding
            )
        ),
        "EXISTS": StdLibCall(lambda filepath: _file_exists(filepath)),
        "DELETE": StdLibCall(lambda filepath: _file_delete(filepath)),
        "RENAME": StdLibCall(
            lambda old_path, new_path: _file_rename(old_path, new_path)
        ),
        "SIZE": StdLibCall(lambda filepath: _file_size(filepath)),
        "IS_FILE": StdLibCall(lambda filepath: _file_is_file(filepath)),
        "IS_DIRECTORY": StdLibCall(lambda filepath: _file_is_dir(filepath)),
        "LIST_DIRECTORY": StdLibCall(lambda path=".": _file_list_dir(path)),
        "MAKE_DIRECTORY": StdLibCall(
            lambda path, parents=False, exist_ok=False: _file_make_dir(
                path, parents, exist_ok
            )
        ),
        "REMOVE_DIRECTORY": StdLibCall(lambda path: _file_remove_dir(path)),
        "DELETE_TREE": StdLibCall(lambda path: _file_delete_tree(path)),
    },
}


def _get_current_time_str(tz_aware=False):
    now = (
        datetime.datetime.now(datetime.timezone.utc)
        if tz_aware
        else datetime.datetime.now()
    )
    return now.strftime(DEFAULT_DATETIME_FORMAT)


def _get_current_timestamp():
    return time.time()


def _format_time_str(time_str: str, current_format: str, target_format: str):
    try:
        dt_obj = datetime.datetime.strptime(time_str, current_format)
        return dt_obj.strftime(target_format)
    except ValueError as e:
        raise ValueError(f"Invalid time string or format: {e}")


def _parse_time_to_map(time_str: str, format_str: str):
    """Parses a time string into a map of components."""
    try:
        dt_obj = datetime.datetime.strptime(time_str, format_str)
        return {
            "year": dt_obj.year,
            "month": dt_obj.month,
            "day": dt_obj.day,
            "hour": dt_obj.hour,
            "minute": dt_obj.minute,
            "second": dt_obj.second,
            "microsecond": dt_obj.microsecond,
            "weekday": dt_obj.weekday(),
            "yearday": dt_obj.timetuple().tm_yday,
        }
    except ValueError as e:
        raise ValueError(f"Invalid time string or format for parsing to map: {e}")


def _get_time_components_now():
    """Returns current time as a map of components."""
    now = datetime.datetime.now()
    return {
        "year": now.year,
        "month": now.month,
        "day": now.day,
        "hour": now.hour,
        "minute": now.minute,
        "second": now.second,
        "microsecond": now.microsecond,
        "weekday": now.weekday(),
        "yearday": now.timetuple().tm_yday,
    }


def _file_read(filepath: str, encoding: str = "utf-8"):
    """Reads the content of a file."""
    try:
        with open(filepath, "r", encoding=encoding) as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {filepath}")
    except Exception as e:
        raise IOError(f"Error reading file '{filepath}': {e}")


def _file_write(
    filepath: str, content: str, append: bool = False, encoding: str = "utf-8"
):
    """Writes content to a file. Overwrites by default, appends if append is True."""
    mode = "a" if append else "w"
    try:
        with open(filepath, mode, encoding=encoding) as f:
            f.write(content)
        return True  # Indicate success
    except Exception as e:
        raise IOError(f"Error writing to file '{filepath}': {e}")


def _file_exists(filepath: str):
    """Checks if a file or directory exists."""
    return os.path.exists(filepath)


def _file_delete(filepath: str):
    """Deletes a file."""
    try:
        os.remove(filepath)
        return True  # Indicate success
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {filepath}")
    except IsADirectoryError:
        raise IsADirectoryError(
            f"Cannot delete directory using file delete: {filepath}"
        )
    except Exception as e:
        raise OSError(f"Error deleting file '{filepath}': {e}")


def _file_rename(old_path: str, new_path: str):
    """Renames or moves a file."""
    try:
        os.rename(old_path, new_path)
        return True  # Indicate success
    except FileNotFoundError:
        raise FileNotFoundError(f"Source file not found: {old_path}")
    except FileExistsError:
        raise FileExistsError(f"Destination file already exists: {new_path}")
    except Exception as e:
        raise OSError(f"Error renaming file from '{old_path}' to '{new_path}': {e}")


def _file_size(filepath: str):
    """Returns the size of a file in bytes."""
    try:
        return os.path.getsize(filepath)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {filepath}")
    except Exception as e:
        raise OSError(f"Error getting size of file '{filepath}': {e}")


def _file_is_file(filepath: str):
    """Checks if the given path is a regular file."""
    return os.path.isfile(filepath)


def _file_is_dir(filepath: str):
    """Checks if the given path is a directory."""
    return os.path.isdir(filepath)


def _file_list_dir(path: str = "."):
    """Lists contents of a directory."""
    try:
        return os.listdir(path)
    except FileNotFoundError:
        raise FileNotFoundError(f"Directory not found: {path}")
    except Exception as e:
        raise OSError(f"Error listing directory '{path}': {e}")


def _file_make_dir(path: str, parents: bool = False, exist_ok: bool = False):
    """Creates a directory."""
    try:
        if parents:
            os.makedirs(path, exist_ok=exist_ok)
        else:
            os.mkdir(path)
        return True
    except FileExistsError:
        if not exist_ok:
            raise FileExistsError(f"Directory already exists: {path}")
        return True  # if exist_ok, it's fine
    except Exception as e:
        raise OSError(f"Error creating directory '{path}': {e}")


def _file_remove_dir(path: str):
    """Removes an empty directory."""
    try:
        os.rmdir(path)
        return True
    except FileNotFoundError:
        raise FileNotFoundError(f"Directory not found: {path}")
    except OSError as e:
        if "Directory not empty" in str(e):  # Specific check for non-empty dir
            raise OSError(
                f"Directory not empty: {path}. Use File.DELETE_TREE for non-empty directories."
            )
        raise OSError(f"Error removing directory '{path}': {e}")
    except Exception as e:
        raise OSError(f"Error removing directory '{path}': {e}")


def _file_delete_tree(path: str):
    """Recursively deletes a directory tree (use with caution!)."""
    import shutil

    try:
        shutil.rmtree(path)
        return True
    except FileNotFoundError:
        raise FileNotFoundError(f"Path not found: {path}")
    except Exception as e:
        raise OSError(f"Error deleting directory tree '{path}': {e}")


def _shuffle(x):
    shuffle(x)
    return x


# TODO:

"""
libraries = {
    "String": {
        "upper"
        "lower"
        "len"
        "trim"
        "replace"
        "split"
        "join"
        "contains"
        "starts_with"
        "ends_with"
        "repeat"
        "reverse"
        "substr"
        "pad_left"
        "pad_right"
        "capitalize"
        "title"
    },
    THIS WILL BE HARD
    "Type": {
        "is_int"
        "is_float"
        "is_string"
        "is_list"
        "is_bool"
        "get"
        "to_int"
        "to_float"
        "to_string"
        "to_bool"
    },
    "List": {
        "sort"
        "reverse"
        "map"
        "filter"
        "reduce"
        "find"
        "count"
        "sum"
        "avg"
        "zip"
        "enumerate"
        "slice"
        "concat"
        "unique"
    },
    # These will be tricky
    "System": {"args" "env" "exec"},
}
"""
