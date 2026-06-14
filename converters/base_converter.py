# converters/base_converter.py
"""转换器基类"""
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Optional

class BaseConverter(ABC):
    """转换器基类"""

    def __init__(self, output_dir: Optional[str] = None):
        """
        初始化转换器

        Args:
            output_dir: 输出目录，如果为 None 则输出到原文件同目录
        """
        self.output_dir = Path(output_dir) if output_dir else None

    @abstractmethod
    def convert(self, file_path: str) -> str:
        """
        转换文件为 Markdown

        Args:
            file_path: 源文件路径

        Returns:
            Markdown 内容
        """
        pass

    def get_output_path(self, file_path: str) -> Path:
        """
        获取输出文件路径

        Args:
            file_path: 源文件路径

        Returns:
            输出文件路径（.md 文件）
        """
        source_path = Path(file_path)

        if self.output_dir:
            # 输出到指定目录
            output_path = self.output_dir / f"{source_path.stem}.md"
        else:
            # 输出到原文件同目录
            output_path = source_path.parent / f"{source_path.stem}.md"

        return output_path

    def ensure_output_dir(self, output_path: Path) -> None:
        """确保输出目录存在"""
        output_path.parent.mkdir(parents=True, exist_ok=True)

    def save_markdown(self, content: str, file_path: str) -> Path:
        """
        保存 Markdown 文件

        Args:
            content: Markdown 内容
            file_path: 源文件路径

        Returns:
            保存的文件路径
        """
        output_path = self.get_output_path(file_path)
        self.ensure_output_dir(output_path)

        output_path.write_text(content, encoding='utf-8')

        return output_path
