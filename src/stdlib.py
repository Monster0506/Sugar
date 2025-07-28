import datetime
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
    "Time": {"now" "sleep" "format" "parse"},
    "File": {"read" "write" "exists" "delete" "rename" "size"},
    "System": {"args" "exit" "env" "exec"},
}
"""
