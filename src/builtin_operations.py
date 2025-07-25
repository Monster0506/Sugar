import functools
from typing import Any


def _set_and_return_array(arr: list[Any], i: int, v: Any) -> list[Any]:
    arr[i] = v
    return arr


def _set_and_return_dict(d, key, value):
    d[key] = value
    return d


array_operations = {
    "ADD": (lambda arr, val: arr.append(val)),
    "LENGTH": (lambda arr: len(arr)),
    "GET": (lambda arr, i: arr[i]),
    "INSERT": (lambda arr, i, val: arr.insert(i, val)),
    "REMOVE": (lambda arr, i: arr.pop(i)),
    "REVERSE": (lambda arr: arr.reverse()),
    "FILTER": (lambda arr, func: list(filter(func, arr))),
    "MAP": (lambda arr, func: list(map(func, arr))),
    "INDEX_OF": (lambda arr, val: arr.index(val) if val in arr else -1),
    "ANY": (lambda arr, func: any(func(x) for x in arr)),
    "ALL": (lambda arr, func: all(func(x) for x in arr)),
    "SET": (_set_and_return_array),
    "CONTAINS": (lambda arr, val: val in arr),
    "SLICE": (lambda arr, start, end: arr[start:end]),
    "REDUCE": (lambda arr, func, initial: functools.reduce(func, arr, initial)),
    "SUM": (lambda arr: sum(arr)),
    "SORT": (lambda arr: arr.sort()),
}


class _StringOperations:
    @staticmethod
    def _set(s: str, i: int, v: str) -> str:
        result = s[:i] + v + s[i + 1 :]
        return result

    @staticmethod
    def _insert(s: str, i: int, v: str) -> str:
        result = s[:i] + v + s[i:]
        return result

    @staticmethod
    def _remove(s: str, i: int) -> str:
        result = s[:i] + s[i + 1 :]
        return result

    @staticmethod
    def _reverse(s: str) -> str:
        result = s[::-1]
        return result

    @staticmethod
    def _sort(s: str) -> str:
        result = "".join(sorted(s))
        return result


str_operations = {
    "ADD": (lambda s, val: s + val),
    "LENGTH": (lambda s: len(s)),
    "GET": (lambda s, i: s[i]),
    "INSERT": (_StringOperations._insert),
    "REMOVE": (_StringOperations._remove),
    "REVERSE": (_StringOperations._reverse),
    "FILTER": (lambda s, func: "".join(filter(func, s))),
    "MAP": (lambda s, func: "".join(map(func, s))),
    "INDEX_OF": (lambda s, val: s.index(val) if val in s else -1),
    "ANY": (lambda s, val: val in s),
    "ALL": (lambda s, func: all(func(x) for x in s)),
    "SET": (_StringOperations._set),
    "CONTAINS": (lambda s, val: val in s),
    "SLICE": (lambda s, start, end: s[start:end]),
    "SORT": (_StringOperations._sort),
    "UPPER": (lambda s: s.upper()),
    "LOWER": (lambda s: s.lower()),
}


def _raise_value_error(key, d):
    raise ValueError(f"{key} missing from {d}")


def _safe_get(d, key):
    print(f"safe_get with {key=}, {d=}")
    if key in d:
        return d.get(key)
    raise KeyError(f"{key} missing from {d}")


map_operations = {
    "GET": (_safe_get),
    "SET": (_set_and_return_dict),
    "KEYS": (lambda d: list(d.keys())),
    "VALUES": (lambda d: list(d.values())),
    "ITEMS": (lambda d: list(d.items())),
    "HAS_KEY": (lambda d, key: key in d),
    "REMOVE_KEY": (lambda d, key: d.pop(key, None)),
    "LENGTH": (lambda d: len(d)),
    "UPDATE": (lambda d1, d2: d1.update(d2) or d1),
    "CLEAR": (lambda d: d.clear() or d),
    "GET_DEFAULT": (lambda d, key, default: d.get(key, default)),
}
