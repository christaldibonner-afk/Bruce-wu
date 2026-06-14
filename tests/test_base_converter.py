# tests/test_base_converter.py
import pytest
import tempfile
from pathlib import Path
from converters.base_converter import BaseConverter

class ConcreteConverter(BaseConverter):
    """具体转换器实现（用于测试）"""

    def convert(self, file_path: str) -> str:
        return "# Test Markdown"

def test_base_converter_init():
    """测试转换器初始化"""
    with tempfile.TemporaryDirectory() as tmpdir:
        converter = ConcreteConverter(tmpdir)
        assert converter.output_dir == Path(tmpdir)

def test_get_output_path():
    """测试获取输出路径"""
    with tempfile.TemporaryDirectory() as tmpdir:
        converter = ConcreteConverter(tmpdir)

        output_path = converter.get_output_path("/path/to/document.pdf")
        assert output_path.suffix == ".md"
        assert output_path.stem == "document"

def test_ensure_output_dir():
    """测试确保输出目录存在"""
    with tempfile.TemporaryDirectory() as tmpdir:
        converter = ConcreteConverter(tmpdir)

        output_path = converter.get_output_path("/path/to/document.pdf")
        converter.ensure_output_dir(output_path)

        assert output_path.parent.exists()
