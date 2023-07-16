import time
from .logger import get_logger


logger = get_logger(__name__)


def time_func(func, *args):
    start_time = time.time()
    result = func(*args)
    end_time = time.time()
    logger.info(
        f"Function {func.__name__} took {end_time - start_time} seconds to execute."
    )
    return result


async def time_coro(coro, *args):
    start_time = time.time()
    result = await coro(*args)
    end_time = time.time()
    logger.info(
        f"Function {coro.__name__} took {end_time - start_time} seconds to execute."
    )
    return result
