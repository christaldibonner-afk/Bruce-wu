# tests/test_file_detector.py
import pytest
from utils.file_detector import detect_file_type, is_pdf, is_word, is_excel

def test_detect_pdf_type():
    """测试 PDF 文件类型检测"""
    assert detect_file_type("document.pdf") == "pdf"
    assert detect_file_type("DOCUMENT.PDF") == "pdf"

def test_detect_word_type():
    """测试 Word 文件类型检测"""
    assert detect_file_type("document.docx") == "word"
    assert detect_file_type("DOCUMENT.DOCX") == "word"

def test_detect_excel_type():
    """测试 Excel 文件类型检测"""
    assert detect_file_type("spreadsheet.xlsx") == "excel"
    assert detect_file_type("spreadsheet.xls") == "excel"
    assert detect_file_type("SPREADSHEET.XLSX") == "excel"

def test_detect_unsupported_type():
    """测试不支持的文件类型"""
    assert detect_file_type("file.txt") is None
    assert detect_file_type("file.pptx") is None

def test_is_pdf():
    """测试 is_pdf 辅助函数"""
    assert is_pdf("file.pdf") is True
    assert is_pdf("file.docx") is False

def test_is_word():
    """测试 is_word 辅助函数"""
    assert is_word("file.docx") is True
    assert is_word("file.pdf") is False

def test_is_excel():
    """测试 is_excel 辅助函数"""
    assert is_excel("file.xlsx") is True
    assert is_excel("file.xls") is True
    assert is_excel("file.pdf") is False
