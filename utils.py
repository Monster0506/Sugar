import logging


def debug_wrapper(func, logger_name=None):
    """
    A decorator that logs the arguments and keyword arguments of a function call.

    Args:
        func (callable): The function to be wrapped.
        logger_name (str, optional): The name of the logger to use. If None,
                                     it will use the module and function name.
                                     Defaults to None.
    """

    def wrapper(*args, **kwargs):
        logger = logging.getLogger(logger_name or f"{func.__module__}.{func.__name__}")
        logger.setLevel(logging.DEBUG)
        # For methods, args[0] is 'self', so we log from args[1:]
        # For regular functions, args[0] is the first argument
        logged_args = args[1:] if hasattr(func, "__self__") else args
        logger.debug(
            f"{func.__name__} called with args: {logged_args!r} and kwargs: {kwargs!r}"
        )
        return func(*args, **kwargs)  # Crucially, call the original function!

    return wrapper


def debug_class_wrapper(cls, logger_name=None):
    """
    A class decorator that applies the debug_wrapper to all callable methods
    within the class.

    Args:
        cls (type): The class to be wrapped.
        logger_name (str, optional): The base name for the logger. If None,
                                     it will use the class name.
                                     Defaults to None.
    """
    for name, method in cls.__dict__.items():
        if callable(method) and not name.startswith(
            "__"
        ):  # Avoid wrapping dunder methods
            # Use a more specific logger name for each method if desired
            method_logger_name = logger_name or cls.__name__
            setattr(cls, name, debug_wrapper(method, method_logger_name))
    return cls
