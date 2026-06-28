"""图片处理工具测试"""
import pytest
import os
import tempfile
from pathlib import Path
from utils.image_handler import ImageHandler


def test_create_image_directory():
    """测试创建图片目录"""
    with tempfile.TemporaryDirectory() as tmpdir:
        handler = ImageHandler(tmpdir)
        img_dir = handler.create_image_directory()

        assert img_dir.exists()
        assert img_dir.name == "assets"
        assert (img_dir / "images").exists()


def test_generate_image_filename():
    """测试生成图片文件名"""
    with tempfile.TemporaryDirectory() as tmpdir:
        handler = ImageHandler(tmpdir)

        # 第一张图片
        filename1 = handler.generate_image_filename("test.png", 0)
        assert filename1 == "test_img_0.png"

        # 第二张图片
        filename2 = handler.generate_image_filename("test.png", 1)
        assert filename2 == "test_img_1.png"


def test_save_image():
    """测试保存图片"""
    with tempfile.TemporaryDirectory() as tmpdir:
        handler = ImageHandler(tmpdir)

        # 创建一个简单的测试图片
        from PIL import Image
        img = Image.new('RGB', (100, 100), color='red')

        # 保存图片
        saved_path = handler.save_image(img, "test.png", 0)

        assert saved_path.exists()
        assert saved_path.name == "test_img_0.png"


def test_get_relative_path():
    """测试获取相对路径"""
    with tempfile.TemporaryDirectory() as tmpdir:
        handler = ImageHandler(tmpdir)

        relative_path = handler.get_relative_path("test_img_0.png")
        assert relative_path == "./assets/images/test_img_0.png"
