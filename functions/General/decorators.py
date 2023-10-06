import functools
import inspect


def check_args_for_percentage(*args):
    """
    Decorator which checks given keyword arguments for decimals.
    """

    def decorator(func):
        func_args_by_name = inspect.getfullargspec(func).args
        indices_of_args = [func_args_by_name.index(arg) for arg in args]

        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            for n in indices_of_args:
                assert args[n] <= 1, n

            return func(*args, **kwargs)

        return wrapped

    return decorator

# TODO: Currently not usable due to circular imports. Fix this