import inspect
import os


def debug_print(*to_print):
    frame = inspect.currentframe().f_back
    line_number = frame.f_lineno
    print(f"\033[34m[DEBUG]\033[0m :{line_number} -", *to_print)
