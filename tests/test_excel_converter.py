# tests/test_excel_converter.py
import pytest
import tempfile
from pathlib import Path
from converters.excel_converter import ExcelConverter

def test_convert_simple_excel():
    """测试转换简单 Excel"""
    fixtures_dir = Path(__file__).parent / "fixtures"
    excel_path = fixtures_dir / "sample.xlsx"

    if not excel_path.exists():
        pytest.skip("测试文件不存在")

    with tempfile.TemporaryDirectory() as tmpdir:
        converter = ExcelConverter(tmpdir)
        markdown = converter.convert(str(excel_path))

        # 检查是否包含工作表标题
        assert "## Sheet1" in markdown
        assert "## Sheet2" in markdown

        # 检查是否包含表格
        assert "|" in markdown  # Markdown 表格标记

        # 检查是否包含数据
        assert "张三" in markdown
        assert "李四" in markdown

def test_save_converted_excel():
    """测试保存转换后的 Excel"""
    fixtures_dir = Path(__file__).parent / "fixtures"
    excel_path = fixtures_dir / "sample.xlsx"

    if not excel_path.exists():
        pytest.skip("测试文件不存在")

    with tempfile.TemporaryDirectory() as tmpdir:
        converter = ExcelConverter(tmpdir)
        markdown = converter.convert(str(excel_path))

        # 保存文件
        output_path = converter.save_markdown(markdown, str(excel_path))

        # 验证文件存在
        assert output_path.exists()
        assert output_path.suffix == ".md"

        # 验证内容
        saved_content = output_path.read_text(encoding='utf-8')
        assert saved_content == markdown
