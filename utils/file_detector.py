"""文件类型检测模块"""
import os
from typing import Optional


def detect_file_type(file_path: str) -> Optional[str]:
    """
    检测文件类型

    Args:
        file_path: 文件路径

    Returns:
        文件类型：'pdf', 'word', 'excel' 或 None
    """
    if not file_path:
        return None

    # 获取文件扩展名（小写）
    ext = os.path.splitext(file_path)[1].lower()

    # 类型映射
    type_map = {
        '.pdf': 'pdf',
        '.docx': 'word',
        '.xlsx': 'excel',
        '.xls': 'excel'
    }

    return type_map.get(ext)


def is_pdf(file_path: str) -> bool:
    """判断是否为 PDF 文件"""
    return detect_file_type(file_path) == 'pdf'


def is_word(file_path: str) -> bool:
    """判断是否为 Word 文件"""
    return detect_file_type(file_path) == 'word'


def is_excel(file_path: str) -> bool:
    """判断是否为 Excel 文件"""
    return detect_file_type(file_path) == 'excel'
