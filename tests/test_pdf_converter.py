"""PDF 转换器测试"""
import pytest
import tempfile
from pathlib import Path
from converters.pdf_converter import PDFConverter


def test_detect_text_pdf():
    """测试检测文本型 PDF"""
    fixtures_dir = Path(__file__).parent / "fixtures"
    pdf_path = fixtures_dir / "sample_text.pdf"

    if not pdf_path.exists():
        pytest.skip("测试文件不存在")

    converter = PDFConverter()
    pdf_type = converter.detect_pdf_type(str(pdf_path))

    assert pdf_type == "text"


def test_convert_text_pdf():
    """测试转换文本型 PDF"""
    fixtures_dir = Path(__file__).parent / "fixtures"
    pdf_path = fixtures_dir / "sample_text.pdf"

    if not pdf_path.exists():
        pytest.skip("测试文件不存在")

    with tempfile.TemporaryDirectory() as tmpdir:
        converter = PDFConverter(tmpdir)
        markdown = converter.convert(str(pdf_path))

        # 检查是否包含文本内容
        assert "Test Document" in markdown or "test" in markdown.lower()


def test_save_converted_pdf():
    """测试保存转换后的 PDF"""
    fixtures_dir = Path(__file__).parent / "fixtures"
    pdf_path = fixtures_dir / "sample_text.pdf"

    if not pdf_path.exists():
        pytest.skip("测试文件不存在")

    with tempfile.TemporaryDirectory() as tmpdir:
        converter = PDFConverter(tmpdir)
        markdown = converter.convert(str(pdf_path))

        # 保存文件
        output_path = converter.save_markdown(markdown, str(pdf_path))

        # 验证文件存在
        assert output_path.exists()
        assert output_path.suffix == ".md"
