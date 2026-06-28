# converters/excel_converter.py
"""Excel 转 Markdown 转换器"""
import pandas as pd
from pathlib import Path
from typing import Optional
from converters.base_converter import BaseConverter

class ExcelConverter(BaseConverter):
    """Excel 转 Markdown 转换器"""

    def convert(self, file_path: str) -> str:
        """
        将 Excel 文件转换为 Markdown

        Args:
            file_path: Excel 文件路径

        Returns:
            Markdown 内容
        """
        # 读取 Excel 文件
        excel_file = pd.ExcelFile(file_path)

        markdown_parts = []

        # 添加主标题
        source_name = Path(file_path).stem
        markdown_parts.append(f"# {source_name}\n")

        # 处理每个工作表
        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(excel_file, sheet_name=sheet_name)

            # 添加工作表标题
            markdown_parts.append(f"\n## {sheet_name}\n")

            # 转换为 Markdown 表格
            # 处理空值
            df = df.fillna('')

            # 转换为 Markdown
            table_md = df.to_markdown(index=False, tablefmt='pipe')

            if table_md:
                markdown_parts.append(table_md)
                markdown_parts.append("\n")

        return '\n'.join(markdown_parts)
