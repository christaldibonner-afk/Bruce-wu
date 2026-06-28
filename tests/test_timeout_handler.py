# tests/test_timeout_handler.py
import pytest
import time
from utils.timeout_handler import run_with_timeout, TimeoutError

def test_function_completes_within_timeout():
    """测试函数在超时时间内完成"""
    def quick_function():
        return "success"

    result = run_with_timeout(quick_function, timeout=5)
    assert result == "success"

def test_function_times_out():
    """测试函数超时"""
    def slow_function():
        time.sleep(10)
        return "success"

    with pytest.raises(TimeoutError):
        run_with_timeout(slow_function, timeout=1)

def test_function_with_args():
    """测试带参数的函数"""
    def add(a, b):
        return a + b

    result = run_with_timeout(add, timeout=5, args=(2, 3))
    assert result == 5

def test_function_with_kwargs():
    """测试带关键字参数的函数"""
    def greet(name, greeting="Hello"):
        return f"{greeting}, {name}!"

    result = run_with_timeout(greet, timeout=5, kwargs={"name": "World"})
    assert result == "Hello, World!"
