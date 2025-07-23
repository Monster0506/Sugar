from typing import Any


def _set_and_return_array(arr: list[Any], i: int, v: Any) -> list[Any]:
    arr[i] = v
    return arr


array_operations = {
    "ADD": (lambda arr, val: arr.append(val)),
    "LENGTH": (lambda arr: len(arr)),
    "GET": (lambda arr, i: arr[i]),
    "INSERT": (lambda arr, i, val: arr.insert(i, val)),
    "REMOVE": (lambda arr, i: arr.pop(i)),
    "REVERSE": (lambda arr: arr.reverse()),
    "FILTER": (lambda arr, func: list(filter(func, arr))),
    "MAP": (lambda arr, func: list(map(func, arr))),
    "FIND": (lambda arr, val: arr.index(val) if val in arr else -1),
    "ANY": (lambda arr, val: any(x == val for x in arr)),
    "ALL": (lambda arr, func: all(func(x) for x in arr)),
    "SET": (_set_and_return_array),
    "CONTAINS": (lambda arr, val: val in arr),
    "INDEX_OF": (lambda arr, val: arr.index(val)),
    "SLICE": (lambda arr, start, end: arr[start, end]),
    "SUM": (lambda arr: sum(arr)),
    "SORT": (lambda arr: arr.sort()),
}

