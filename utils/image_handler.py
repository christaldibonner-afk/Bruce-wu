"""图片处理模块"""
from pathlib import Path
from PIL import Image


class ImageHandler:
    """图片处理类"""

    def __init__(self, base_dir: str):
        """
        初始化图片处理器

        Args:
            base_dir: 基础目录（Markdown 文件所在目录）
        """
        self.base_dir = Path(base_dir)
        self.assets_dir = self.base_dir / "assets"
        self.images_dir = self.assets_dir / "images"

    def create_image_directory(self) -> Path:
        """创建图片存储目录"""
        self.images_dir.mkdir(parents=True, exist_ok=True)
        return self.assets_dir

    def generate_image_filename(self, original_name: str, index: int) -> str:
        """
        生成图片文件名

        Args:
            original_name: 原始文件名
            index: 图片序号

        Returns:
            新的文件名
        """
        # 获取文件名（不含扩展名）和扩展名
        stem = Path(original_name).stem
        ext = Path(original_name).suffix or '.png'

        return f"{stem}_img_{index}{ext}"

    def save_image(self, image: Image.Image, filename: str, index: int) -> Path:
        """
        保存图片

        Args:
            image: PIL Image 对象
            filename: 原始文件名
            index: 图片序号

        Returns:
            保存后的图片路径
        """
        # 确保目录存在
        self.create_image_directory()

        # 生成新文件名
        new_filename = self.generate_image_filename(filename, index)
        save_path = self.images_dir / new_filename

        # 保存图片
        image.save(save_path)

        return save_path

    def get_relative_path(self, filename: str) -> str:
        """
        获取图片在 Markdown 中的相对路径

        Args:
            filename: 图片文件名

        Returns:
            相对路径字符串
        """
        return f"./assets/images/{filename}"
