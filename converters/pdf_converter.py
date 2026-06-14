# converters/pdf_converter.py
"""PDF 转 Markdown 转换器"""
import pdfplumber
import fitz  # pymupdf
from pathlib import Path
from typing import Optional, Tuple
from converters.base_converter import BaseConverter
from utils.image_handler import ImageHandler
from utils.timeout_handler import run_with_timeout, TimeoutError


class PDFConverter(BaseConverter):
    """PDF 转 Markdown 转换器"""

    # 文字密度阈值，低于此值视为图片型 PDF
    TEXT_DENSITY_THRESHOLD = 0.1

    def __init__(self, output_dir: Optional[str] = None, enable_mineru: bool = True):
        """
        初始化 PDF 转换器

        Args:
            output_dir: 输出目录
            enable_mineru: 是否启用 MinerU
        """
        super().__init__(output_dir)
        self.enable_mineru = enable_mineru
        self.image_handler = None

    def detect_pdf_type(self, file_path: str) -> str:
        """
        检测 PDF 类型

        Args:
            file_path: PDF 文件路径

        Returns:
            'text' 或 'image'
        """
        with pdfplumber.open(file_path) as pdf:
            if not pdf.pages:
                return 'text'

            # 检查第一页
            first_page = pdf.pages[0]
            text = first_page.extract_text() or ""

            # 计算文字密度
            page_area = first_page.width * first_page.height
            if page_area == 0:
                return 'text'

            # 估算文字占据的比例
            char_count = len(text.strip())
            density = char_count / (page_area / 1000)  # 归一化

            return 'text' if density >= self.TEXT_DENSITY_THRESHOLD else 'image'

    def convert(self, file_path: str) -> str:
        """
        转换 PDF 文件为 Markdown

        Args:
            file_path: PDF 文件路径

        Returns:
            Markdown 内容
        """
        # 检测 PDF 类型
        pdf_type = self.detect_pdf_type(file_path)

        if pdf_type == 'text':
            return self._convert_text_pdf(file_path)
        else:
            return self._convert_image_pdf(file_path)

    def _convert_text_pdf(self, file_path: str) -> str:
        """转换文本型 PDF"""
        markdown_parts = []

        # 添加主标题
        source_name = Path(file_path).stem
        markdown_parts.append(f"# {source_name}\n")

        # 使用 pdfplumber 提取文本
        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages):
                # 添加页面标记（可选）
                if i > 0:
                    markdown_parts.append(f"\n---\n## 第 {i+1} 页\n")

                # 提取文本
                text = page.extract_text()
                if text:
                    markdown_parts.append(text)

                # 提取表格
                tables = page.extract_tables()
                if tables:
                    markdown_parts.append(self._format_tables(tables))

        return '\n'.join(markdown_parts)

    def _format_tables(self, tables: list) -> str:
        """格式化表格为 Markdown"""
        if not tables:
            return ""

        markdown_parts = []

        for table in tables:
            if not table:
                continue

            # 表头
            header = table[0]
            markdown_parts.append('| ' + ' | '.join(str(cell or '') for cell in header) + ' |')
            markdown_parts.append('| ' + ' | '.join(['---'] * len(header)) + ' |')

            # 数据行
            for row in table[1:]:
                markdown_parts.append('| ' + ' | '.join(str(cell or '') for cell in row) + ' |')

            markdown_parts.append('')

        return '\n'.join(markdown_parts)

    def _convert_image_pdf(self, file_path: str) -> str:
        """转换图片型 PDF（将在任务 9 中完善）"""
        # 降级到 pymupdf
        return self._convert_with_pymupdf(file_path)

    def _convert_with_pymupdf(self, file_path: str) -> str:
        """使用 pymupdf 转换"""
        markdown_parts = []

        source_name = Path(file_path).stem
        markdown_parts.append(f"# {source_name}\n")

        doc = fitz.open(file_path)

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()

            if text.strip():
                markdown_parts.append(text)

        doc.close()

        return '\n'.join(markdown_parts)
