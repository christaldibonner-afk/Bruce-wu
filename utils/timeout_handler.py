"""超时处理模块"""
import threading
from typing import Any, Callable, Optional


class TimeoutError(Exception):
    """超时错误"""
    pass


def run_with_timeout(
    func: Callable,
    timeout: int = 300,
    args: tuple = (),
    kwargs: Optional[dict] = None
) -> Any:
    """
    运行函数并设置超时

    Args:
        func: 要执行的函数
        timeout: 超时时间（秒）
        args: 位置参数
        kwargs: 关键字参数

    Returns:
        函数返回值

    Raises:
        TimeoutError: 超时错误
        Exception: 函数执行错误
    """
    if kwargs is None:
        kwargs = {}

    # 用于存储结果
    result_container = {'result': None, 'error': None, 'completed': False}

    def wrapper():
        try:
            result_container['result'] = func(*args, **kwargs)
            result_container['completed'] = True
        except Exception as e:
            result_container['error'] = e

    # 创建线程
    thread = threading.Thread(target=wrapper)
    thread.daemon = True

    # 启动线程
    thread.start()

    # 等待线程完成或超时
    thread.join(timeout=timeout)

    # 检查是否超时
    if thread.is_alive():
        raise TimeoutError(f"Function {func.__name__} timed out after {timeout} seconds")

    # 检查是否完成
    if result_container['completed']:
        return result_container['result']
    elif result_container['error']:
        raise result_container['error']
    else:
        raise Exception("No result returned from function")
