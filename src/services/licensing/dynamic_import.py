from typing import Callable


def dynamic_import(full_function_name: str) -> Callable:
    """performs a dynamic import of a function given by its 'full path'"""
    mod_n, fun_n = full_function_name.rsplit(".", 1)
    return getattr(__import__(mod_n, fromlist=[fun_n]), fun_n)
