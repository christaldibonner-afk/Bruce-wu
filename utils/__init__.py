"""工具模块"""
from utils.file_detector import detect_file_type, is_pdf, is_word, is_excel
from utils.image_handler import ImageHandler
from utils.timeout_handler import run_with_timeout, TimeoutError

__all__ = [
    'detect_file_type',
    'is_pdf',
    'is_word',
    'is_excel',
    'ImageHandler',
    'run_with_timeout',
    'TimeoutError'
]
