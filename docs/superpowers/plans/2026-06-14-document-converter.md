# 文档格式转换工具实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 创建一个 Web 应用，将 PDF、Word、Excel 文档转换为 Markdown 格式，支持拖拽上传、超时降级、MinerU OCR 等功能。

**架构：** Python + Gradio Web 界面，采用模块化设计，转换器模块独立封装，工具模块提供超时处理、图片处理等通用功能。

**技术栈：** Python 3.8+, Gradio 4.x, pdfplumber, pymupdf, mammoth, python-docx, pandas, openpyxl, magic-pdf (MinerU)

---

## 文件结构

**将要创建的文件及其职责：**

```
项目根目录/
├── requirements.txt                    # 项目依赖
├── app.py                             # Gradio 主程序，界面和事件处理
├── converters/
│   ├── __init__.py                    # 导出所有转换器
│   ├── base_converter.py              # 转换器基类和通用方法
│   ├── pdf_converter.py               # PDF 转 Markdown（文本型/图片型）
│   ├── word_converter.py              # Word 转 Markdown
│   └── excel_converter.py             # Excel 转 Markdown
├── utils/
│   ├── __init__.py                    # 导出所有工具
│   ├── timeout_handler.py             # 超时处理和进程管理
│   ├── image_handler.py               # 图片提取和保存
│   └── file_detector.py               # 文件类型检测
└── tests/
    ├── __init__.py
    ├── test_pdf_converter.py          # PDF 转换器测试
    ├── test_word_converter.py         # Word 转换器测试
    ├── test_excel_converter.py        # Excel 转换器测试
    └── fixtures/                      # 测试数据目录
```

---

## 任务 1：项目初始化和依赖配置

**文件：**
- 创建：`requirements.txt`

- [ ] **步骤 1：创建 requirements.txt**

```python
# Web 界面
gradio>=4.0.0

# PDF 处理
pdfplumber>=0.10.0
pymupdf>=1.23.0

# Word 处理
mammoth>=1.6.0
python-docx>=1.1.0

# Excel 处理
pandas>=2.0.0
openpyxl>=3.1.0

# 图片处理
Pillow>=10.0.0

# MinerU (图片型 PDF OCR)
magic-pdf[full]>=0.6.0

# 测试
pytest>=7.0.0
```

- [ ] **步骤 2：创建项目目录结构**

```bash
mkdir -p converters utils tests/fixtures logs
touch converters/__init__.py utils/__init__.py tests/__init__.py
```

---

## 任务 2：文件类型检测工具

**文件：**
- 创建：`utils/file_detector.py`
- 创建：`tests/test_file_detector.py`

- [ ] **步骤 1：编写文件类型检测测试**

```python
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
```

- [ ] **步骤 2：运行测试验证失败**

```bash
pytest tests/test_file_detector.py -v
```

预期：FAIL，报错 "ModuleNotFoundError: No module named 'utils.file_detector'"

- [ ] **步骤 3：实现文件类型检测**

```python
# utils/file_detector.py
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
```

- [ ] **步骤 4：运行测试验证通过**

```bash
pytest tests/test_file_detector.py -v
```

预期：PASS

- [ ] **步骤 5：Commit**

```bash
git add utils/file_detector.py tests/test_file_detector.py
git commit -m "feat: 添加文件类型检测工具"
```

---

## 任务 3：图片处理工具

**文件：**
- 创建：`utils/image_handler.py`
- 创建：`tests/test_image_handler.py`

- [ ] **步骤 1：编写图片处理测试**

```python
# tests/test_image_handler.py
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
```

- [ ] **步骤 2：运行测试验证失败**

```bash
pytest tests/test_image_handler.py -v
```

预期：FAIL

- [ ] **步骤 3：实现图片处理**

```python
# utils/image_handler.py
"""图片处理模块"""
import os
from pathlib import Path
from typing import Optional
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
```

- [ ] **步骤 4：运行测试验证通过**

```bash
pytest tests/test_image_handler.py -v
```

预期：PASS

- [ ] **步骤 5：Commit**

```bash
git add utils/image_handler.py tests/test_image_handler.py
git commit -m "feat: 添加图片处理工具"
```

---

## 任务 4：超时处理工具

**文件：**
- 创建：`utils/timeout_handler.py`
- 创建：`tests/test_timeout_handler.py`

- [ ] **步骤 1：编写超时处理测试**

```python
# tests/test_timeout_handler.py
import pytest
import time
from utils.timeout_handler import run_with_timeout, TimeoutError

def test_function_completes_within_timeout():
    """测试函数在超时时间内完成"""
    def quick_function():
        return "success"

    result = run_with_timeout(quick_function, timeout=5)
    assert result == "success"

def test_function_times_out():
    """测试函数超时"""
    def slow_function():
        time.sleep(10)
        return "success"

    with pytest.raises(TimeoutError):
        run_with_timeout(slow_function, timeout=1)

def test_function_with_args():
    """测试带参数的函数"""
    def add(a, b):
        return a + b

    result = run_with_timeout(add, timeout=5, args=(2, 3))
    assert result == 5

def test_function_with_kwargs():
    """测试带关键字参数的函数"""
    def greet(name, greeting="Hello"):
        return f"{greeting}, {name}!"

    result = run_with_timeout(greet, timeout=5, kwargs={"name": "World"})
    assert result == "Hello, World!"
```

- [ ] **步骤 2：运行测试验证失败**

```bash
pytest tests/test_timeout_handler.py -v
```

预期：FAIL

- [ ] **步骤 3：实现超时处理**

```python
# utils/timeout_handler.py
"""超时处理模块"""
import multiprocessing
from typing import Any, Callable, Optional
from functools import wraps

class TimeoutError(Exception):
    """超时错误"""
    pass

def _worker(func: Callable, args: tuple, kwargs: dict, queue: multiprocessing.Queue):
    """工作进程函数"""
    try:
        result = func(*args, **kwargs)
        queue.put(('success', result))
    except Exception as e:
        queue.put(('error', str(e)))

def run_with_timeout(
    func: Callable,
    timeout: int = 300,
    args: tuple = (),
    kwargs: Optional[dict] = None
) -> Any:
    """
    运行函数并设置超时

    Args:
        func: 要执行的函数
        timeout: 超时时间（秒）
        args: 位置参数
        kwargs: 关键字参数

    Returns:
        函数返回值

    Raises:
        TimeoutError: 超时错误
        Exception: 函数执行错误
    """
    if kwargs is None:
        kwargs = {}

    # 创建队列用于进程间通信
    queue = multiprocessing.Queue()

    # 创建工作进程
    process = multiprocessing.Process(
        target=_worker,
        args=(func, args, kwargs, queue)
    )

    # 启动进程
    process.start()

    # 等待进程完成或超时
    process.join(timeout=timeout)

    # 检查是否超时
    if process.is_alive():
        # 超时，强制终止
        process.terminate()
        process.join(timeout=1)

        # 如果还没终止，强制 kill
        if process.is_alive():
            process.kill()
            process.join()

        raise TimeoutError(f"Function {func.__name__} timed out after {timeout} seconds")

    # 获取结果
    if not queue.empty():
        status, result = queue.get()

        if status == 'success':
            return result
        else:
            raise Exception(result)
    else:
        raise Exception("No result returned from function")
```

- [ ] **步骤 4：运行测试验证通过**

```bash
pytest tests/test_timeout_handler.py -v
```

预期：PASS

- [ ] **步骤 5：Commit**

```bash
git add utils/timeout_handler.py tests/test_timeout_handler.py
git commit -m "feat: 添加超时处理工具"
```

---

## 任务 5：转换器基类

**文件：**
- 创建：`converters/base_converter.py`
- 创建：`tests/test_base_converter.py`

- [ ] **步骤 1：编写转换器基类测试**

```python
# tests/test_base_converter.py
import pytest
import tempfile
from pathlib import Path
from converters.base_converter import BaseConverter

class ConcreteConverter(BaseConverter):
    """具体转换器实现（用于测试）"""

    def convert(self, file_path: str) -> str:
        return "# Test Markdown"

def test_base_converter_init():
    """测试转换器初始化"""
    with tempfile.TemporaryDirectory() as tmpdir:
        converter = ConcreteConverter(tmpdir)
        assert converter.output_dir == Path(tmpdir)

def test_get_output_path():
    """测试获取输出路径"""
    with tempfile.TemporaryDirectory() as tmpdir:
        converter = ConcreteConverter(tmpdir)

        output_path = converter.get_output_path("/path/to/document.pdf")
        assert output_path.suffix == ".md"
        assert output_path.stem == "document"

def test_ensure_output_dir():
    """测试确保输出目录存在"""
    with tempfile.TemporaryDirectory() as tmpdir:
        converter = ConcreteConverter(tmpdir)

        output_path = converter.get_output_path("/path/to/document.pdf")
        converter.ensure_output_dir(output_path)

        assert output_path.parent.exists()
```

- [ ] **步骤 2：运行测试验证失败**

```bash
pytest tests/test_base_converter.py -v
```

预期：FAIL

- [ ] **步骤 3：实现转换器基类**

```python
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
```

- [ ] **步骤 4：运行测试验证通过**

```bash
pytest tests/test_base_converter.py -v
```

预期：PASS

- [ ] **步骤 5：Commit**

```bash
git add converters/base_converter.py tests/test_base_converter.py
git commit -m "feat: 添加转换器基类"
```

---

## 任务 6：Excel 转换器

**文件：**
- 创建：`converters/excel_converter.py`
- 创建：`tests/test_excel_converter.py`

- [ ] **步骤 1：创建测试 Excel 文件**

```python
# tests/fixtures/create_test_excel.py
import pandas as pd
from pathlib import Path

def create_test_excel():
    """创建测试用的 Excel 文件"""
    fixtures_dir = Path(__file__).parent

    # 创建简单的 Excel
    df1 = pd.DataFrame({
        '姓名': ['张三', '李四', '王五'],
        '年龄': [25, 30, 35],
        '城市': ['北京', '上海', '广州']
    })

    df2 = pd.DataFrame({
        '产品': ['A', 'B', 'C'],
        '价格': [100, 200, 300]
    })

    with pd.ExcelWriter(fixtures_dir / 'sample.xlsx') as writer:
        df1.to_excel(writer, sheet_name='Sheet1', index=False)
        df2.to_excel(writer, sheet_name='Sheet2', index=False)

if __name__ == '__main__':
    create_test_excel()
```

运行：
```bash
python tests/fixtures/create_test_excel.py
```

- [ ] **步骤 2：编写 Excel 转换器测试**

```python
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
```

- [ ] **步骤 3：运行测试验证失败**

```bash
pytest tests/test_excel_converter.py -v
```

预期：FAIL

- [ ] **步骤 4：实现 Excel 转换器**

```python
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
```

- [ ] **步骤 5：运行测试验证通过**

```bash
pytest tests/test_excel_converter.py -v
```

预期：PASS

- [ ] **步骤 6：Commit**

```bash
git add converters/excel_converter.py tests/test_excel_converter.py tests/fixtures/sample.xlsx
git commit -m "feat: 添加 Excel 转 Markdown 转换器"
```

---

## 任务 7：Word 转换器

**文件：**
- 创建：`converters/word_converter.py`
- 创建：`tests/test_word_converter.py`

- [ ] **步骤 1：创建测试 Word 文件**

由于需要创建 .docx 文件，我们将在测试中使用 python-docx 动态创建。

- [ ] **步骤 2：编写 Word 转换器测试**

```python
# tests/test_word_converter.py
import pytest
import tempfile
from pathlib import Path
from docx import Document
from converters.word_converter import WordConverter

@pytest.fixture
def sample_word_file():
    """创建测试 Word 文件"""
    with tempfile.TemporaryDirectory() as tmpdir:
        doc = Document()
        doc.add_heading('测试文档', 0)
        doc.add_heading('第一章', level=1)
        doc.add_paragraph('这是一段测试文本。')
        doc.add_heading('第二章', level=1)
        doc.add_paragraph('这是另一段测试文本。')

        # 添加表格
        table = doc.add_table(rows=2, cols=2)
        table.cell(0, 0).text = '姓名'
        table.cell(0, 1).text = '年龄'
        table.cell(1, 0).text = '张三'
        table.cell(1, 1).text = '25'

        file_path = Path(tmpdir) / "test.docx"
        doc.save(str(file_path))

        yield str(file_path)

def test_convert_word_document(sample_word_file):
    """测试转换 Word 文档"""
    with tempfile.TemporaryDirectory() as tmpdir:
        converter = WordConverter(tmpdir)
        markdown = converter.convert(sample_word_file)

        # 检查是否包含标题
        assert "# 测试文档" in markdown
        assert "## 第一章" in markdown
        assert "## 第二章" in markdown

        # 检查是否包含段落
        assert "测试文本" in markdown

        # 检查是否包含表格
        assert "|" in markdown
        assert "张三" in markdown

def test_save_converted_word(sample_word_file):
    """测试保存转换后的 Word"""
    with tempfile.TemporaryDirectory() as tmpdir:
        converter = WordConverter(tmpdir)
        markdown = converter.convert(sample_word_file)

        # 保存文件
        output_path = converter.save_markdown(markdown, sample_word_file)

        # 验证文件存在
        assert output_path.exists()
        assert output_path.suffix == ".md"
```

- [ ] **步骤 3：运行测试验证失败**

```bash
pytest tests/test_word_converter.py -v
```

预期：FAIL

- [ ] **步骤 4：实现 Word 转换器**

```python
# converters/word_converter.py
"""Word 转 Markdown 转换器"""
import mammoth
from docx import Document
from pathlib import Path
from typing import Optional, List
from converters.base_converter import BaseConverter
from utils.image_handler import ImageHandler

class WordConverter(BaseConverter):
    """Word 转 Markdown 转换器"""

    def convert(self, file_path: str) -> str:
        """
        将 Word 文件转换为 Markdown

        Args:
            file_path: Word 文件路径

        Returns:
            Markdown 内容
        """
        # 使用 mammoth 转换主体内容
        with open(file_path, 'rb') as f:
            result = mammoth.extract_raw_text(f)
            main_content = result.value

        # 使用 python-docx 补充结构信息
        doc = Document(file_path)

        # 构建最终 Markdown
        markdown_parts = []

        # 添加主标题
        source_name = Path(file_path).stem
        markdown_parts.append(f"# {source_name}\n")

        # 处理段落
        for paragraph in doc.paragraphs:
            if paragraph.style.name.startswith('Heading'):
                # 处理标题
                level = self._get_heading_level(paragraph.style.name)
                markdown_parts.append(f"\n{'#' * level} {paragraph.text}\n")
            else:
                # 处理普通段落
                if paragraph.text.strip():
                    markdown_parts.append(f"{paragraph.text}\n")

        # 处理表格
        tables_md = self._process_tables(doc.tables)
        if tables_md:
            markdown_parts.append("\n" + tables_md)

        return '\n'.join(markdown_parts)

    def _get_heading_level(self, style_name: str) -> int:
        """获取标题级别"""
        if 'Heading 1' in style_name or '标题 1' in style_name:
            return 2
        elif 'Heading 2' in style_name or '标题 2' in style_name:
            return 3
        elif 'Heading 3' in style_name or '标题 3' in style_name:
            return 4
        else:
            return 2  # 默认二级标题

    def _process_tables(self, tables: List) -> str:
        """处理表格"""
        if not tables:
            return ""

        markdown_parts = []

        for table in tables:
            rows = []

            # 提取表格数据
            for row in table.rows:
                cells = [cell.text.strip() for cell in row.cells]
                rows.append(cells)

            if rows:
                # 生成 Markdown 表格
                # 表头
                header = rows[0]
                markdown_parts.append('| ' + ' | '.join(header) + ' |')
                markdown_parts.append('| ' + ' | '.join(['---'] * len(header)) + ' |')

                # 数据行
                for row in rows[1:]:
                    markdown_parts.append('| ' + ' | '.join(row) + ' |')

                markdown_parts.append('')

        return '\n'.join(markdown_parts)
```

- [ ] **步骤 5：运行测试验证通过**

```bash
pytest tests/test_word_converter.py -v
```

预期：PASS

- [ ] **步骤 6：Commit**

```bash
git add converters/word_converter.py tests/test_word_converter.py
git commit -m "feat: 添加 Word 转 Markdown 转换器"
```

---

## 任务 8：PDF 转换器（文本型 PDF）

**文件：**
- 创建：`converters/pdf_converter.py`
- 创建：`tests/test_pdf_converter.py`（第 1 部分）

- [ ] **步骤 1：创建测试 PDF 文件**

使用 reportlab 创建测试 PDF：

```bash
pip install reportlab
```

```python
# tests/fixtures/create_test_pdf.py
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from pathlib import Path

def create_text_pdf():
    """创建文本型测试 PDF"""
    fixtures_dir = Path(__file__).parent
    pdf_path = fixtures_dir / "sample_text.pdf"

    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    width, height = letter

    # 第一页
    c.setFont("Helvetica-Bold", 24)
    c.drawString(1*inch, height - 1*inch, "Test Document")

    c.setFont("Helvetica", 12)
    c.drawString(1*inch, height - 2*inch, "This is a test PDF document.")
    c.drawString(1*inch, height - 2.3*inch, "It contains multiple lines of text.")
    c.drawString(1*inch, height - 2.6*inch, "Used for testing the PDF converter.")

    c.save()

    print(f"Created: {pdf_path}")

if __name__ == '__main__':
    create_text_pdf()
```

运行：
```bash
python tests/fixtures/create_test_pdf.py
```

- [ ] **步骤 2：编写 PDF 转换器测试（文本型）**

```python
# tests/test_pdf_converter.py
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
```

- [ ] **步骤 3：运行测试验证失败**

```bash
pytest tests/test_pdf_converter.py -v
```

预期：FAIL

- [ ] **步骤 4：实现 PDF 转换器（文本型部分）**

```python
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
```

- [ ] **步骤 5：运行测试验证通过**

```bash
pytest tests/test_pdf_converter.py -v
```

预期：PASS

- [ ] **步骤 6：Commit**

```bash
git add converters/pdf_converter.py tests/test_pdf_converter.py tests/fixtures/sample_text.pdf
git commit -m "feat: 添加 PDF 转 Markdown 转换器（文本型）"
```

---

## 任务 9：PDF 转换器（图片型 PDF + MinerU）

**文件：**
- 修改：`converters/pdf_converter.py`
- 修改：`tests/test_pdf_converter.py`

- [ ] **步骤 1：编写 MinerU 集成测试**

```python
# tests/test_pdf_converter.py（继续添加）
import pytest
from converters.pdf_converter import PDFConverter

def test_mineru_available():
    """测试 MinerU 是否可用"""
    try:
        from magic_pdf.data.data_reader_writer import FileBasedDataReader
        mineru_available = True
    except ImportError:
        mineru_available = False

    if not mineru_available:
        pytest.skip("MinerU 未安装")

def test_convert_with_fallback():
    """测试降级机制"""
    fixtures_dir = Path(__file__).parent / "fixtures"
    pdf_path = fixtures_dir / "sample_text.pdf"

    if not pdf_path.exists():
        pytest.skip("测试文件不存在")

    with tempfile.TemporaryDirectory() as tmpdir:
        # 禁用 MinerU，测试降级
        converter = PDFConverter(tmpdir, enable_mineru=False)
        markdown = converter.convert(str(pdf_path))

        # 应该使用 pdfplumber
        assert len(markdown) > 0
```

- [ ] **步骤 2：运行测试验证失败**

```bash
pytest tests/test_pdf_converter.py::test_convert_with_fallback -v
```

预期：PASS（已有实现）

- [ ] **步骤 3：完善图片型 PDF 处理**

```python
# converters/pdf_converter.py（更新 _convert_image_pdf 方法）
def _convert_image_pdf(self, file_path: str) -> str:
    """
    转换图片型 PDF

    优先使用 MinerU，失败则降级到 pymupdf
    """
    # 尝试使用 MinerU
    if self.enable_mineru:
        try:
            result = self._convert_with_mineru(file_path)
            if result:
                return result
        except Exception as e:
            print(f"MinerU 转换失败: {e}")

    # 降级到 pymupdf
    print("降级到 pymupdf 处理")
    return self._convert_with_pymupdf(file_path)

def _convert_with_mineru(self, file_path: str) -> Optional[str]:
    """
    使用 MinerU 转换图片型 PDF

    Returns:
        Markdown 内容，失败返回 None
    """
    try:
        from magic_pdf.data.data_reader_writer import FileBasedDataReader, FileBasedDataWriter
        from magic_pdf.data.dataset import PymuDocDataset
        from magic_pdf.model.doc_analyze_by_custom_model import doc_analyze

        # 创建读取器
        reader = FileBasedDataReader("")
        pdf_bytes = reader.read(file_path)

        # 创建数据集
        ds = PymuDocDataset(pdf_bytes)

        # 分析文档
        if ds.classify() == "ocr":
            infer_result = ds.apply_ocr()
        else:
            infer_result = ds.apply()

        # 获取 Markdown 内容
        content_list = infer_result.get_content_list(
            FileBasedDataWriter(""),
            os.path.basename(file_path).replace('.pdf', '')
        )

        # 提取文本
        markdown_parts = []
        for item in content_list:
            if item.get('type') == 'text':
                markdown_parts.append(item.get('text', ''))

        return '\n'.join(markdown_parts) if markdown_parts else None

    except ImportError:
        print("MinerU 未安装")
        return None
    except Exception as e:
        print(f"MinerU 处理出错: {e}")
        return None
```

- [ ] **步骤 4：添加超时处理**

```python
# converters/pdf_converter.py（添加超时包装）
def convert_with_timeout(self, file_path: str, timeout: int = 300) -> str:
    """
    带超时的转换

    Args:
        file_path: PDF 文件路径
        timeout: 超时时间（秒）

    Returns:
        Markdown 内容

    Raises:
        TimeoutError: 超时错误
    """
    try:
        return run_with_timeout(
            self.convert,
            timeout=timeout,
            args=(file_path,)
        )
    except TimeoutError:
        # 尝试降级方案
        return self._convert_with_pymupdf(file_path)
```

- [ ] **步骤 5：运行测试验证通过**

```bash
pytest tests/test_pdf_converter.py -v
```

预期：PASS

- [ ] **步骤 6：Commit**

```bash
git add converters/pdf_converter.py tests/test_pdf_converter.py
git commit -m "feat: 添加图片型 PDF 处理和 MinerU 集成"
```

---

## 任务 10：转换器模块初始化

**文件：**
- 创建：`converters/__init__.py`

- [ ] **步骤 1：编写模块导出**

```python
# converters/__init__.py
"""转换器模块"""
from converters.base_converter import BaseConverter
from converters.pdf_converter import PDFConverter
from converters.word_converter import WordConverter
from converters.excel_converter import ExcelConverter

__all__ = [
    'BaseConverter',
    'PDFConverter',
    'WordConverter',
    'ExcelConverter'
]
```

- [ ] **步骤 2：编写工具模块导出**

```python
# utils/__init__.py
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
```

- [ ] **步骤 3：Commit**

```bash
git add converters/__init__.py utils/__init__.py
git commit -m "feat: 添加模块导出"
```

---

## 任务 11：主应用程序（Gradio 界面）

**文件：**
- 创建：`app.py`

- [ ] **步骤 1：创建主应用文件**

```python
# app.py
#!/usr/bin/env python3
"""
Bruce Wu 的转化小站
文档格式转换工具 - 支持 PDF、Word、Excel 转 Markdown
"""
import os
import tempfile
import zipfile
from pathlib import Path
from typing import List, Tuple, Optional
import gradio as gr

from converters import PDFConverter, WordConverter, ExcelConverter
from utils import detect_file_type

# 配置
OUTPUT_DIR = None  # None 表示输出到原文件同目录
MAX_CONCURRENT = 3  # 最大并发数


def convert_single_file(
    file_path: str,
    enable_mineru: bool = True,
    timeout: int = 300
) -> Tuple[Optional[str], Optional[str]]:
    """
    转换单个文件

    Args:
        file_path: 文件路径
        enable_mineru: 是否启用 MinerU
        timeout: 超时时间（秒）

    Returns:
        (输出文件路径, 错误信息)
    """
    try:
        # 检测文件类型
        file_type = detect_file_type(file_path)

        if not file_type:
            return None, f"不支持的文件格式: {Path(file_path).suffix}"

        # 创建对应的转换器
        if file_type == 'pdf':
            converter = PDFConverter(OUTPUT_DIR, enable_mineru=enable_mineru)
        elif file_type == 'word':
            converter = WordConverter(OUTPUT_DIR)
        elif file_type == 'excel':
            converter = ExcelConverter(OUTPUT_DIR)
        else:
            return None, f"不支持的文件类型: {file_type}"

        # 执行转换
        if file_type == 'pdf':
            # PDF 需要超时处理
            try:
                markdown = converter.convert_with_timeout(file_path, timeout=timeout)
            except Exception as e:
                return None, f"转换超时或失败: {str(e)}"
        else:
            markdown = converter.convert(file_path)

        # 保存文件
        output_path = converter.save_markdown(markdown, file_path)

        return str(output_path), None

    except Exception as e:
        return None, f"转换失败: {str(e)}"


def convert_files(
    files: List,
    timeout: int,
    enable_mineru: bool,
    progress=gr.Progress()
) -> Tuple[List, str, str]:
    """
    批量转换文件

    Args:
        files: 上传的文件列表
        timeout: 超时时间（秒）
        enable_mineru: 是否启用 MinerU
        progress: Gradio 进度对象

    Returns:
        (输出文件列表, 进度信息, 处理报告)
    """
    if not files:
        return [], "请上传文件", ""

    # 确保文件是列表
    if not isinstance(files, list):
        files = [files]

    output_files = []
    success_count = 0
    failed_files = []

    total = len(files)

    for i, file in enumerate(progress.tqdm(files, desc="转换中")):
        file_path = file.name if hasattr(file, 'name') else file

        progress((i + 1) / total, desc=f"处理文件 {i+1}/{total}: {Path(file_path).name}")

        output_path, error = convert_single_file(
            file_path,
            enable_mineru=enable_mineru,
            timeout=timeout
        )

        if output_path:
            output_files.append(output_path)
            success_count += 1
        else:
            failed_files.append((Path(file_path).name, error))

    # 生成报告
    report = f"总计: {total} 个文件\n"
    report += f"✅ 成功: {success_count} 个\n"
    report += f"❌ 失败: {len(failed_files)} 个\n"

    if failed_files:
        report += "\n失败文件:\n"
        for filename, error in failed_files:
            report += f"- {filename}: {error}\n"

    progress_msg = f"转换完成！成功 {success_count}/{total} 个文件"

    return output_files, progress_msg, report


# 创建 Gradio 界面
with gr.Blocks(
    title="Bruce Wu 的转化小站",
    theme=gr.themes.Soft()
) as app:

    # 标题
    gr.Markdown(
        """
        # 🎉 Bruce Wu 的转化小站 🎉

        支持 PDF、Word、Excel 转 Markdown
        """
    )

    # 文件上传
    file_input = gr.File(
        label="📁 文件上传",
        file_count="multiple",
        file_types=[".pdf", ".docx", ".xlsx", ".xls"]
    )

    # 高级设置
    with gr.Accordion("⚙️ 高级设置", open=False):
        timeout_slider = gr.Slider(
            minimum=60,
            maximum=600,
            value=300,
            step=30,
            label="超时时间（秒）",
            info="图片型 PDF 处理超时时间"
        )
        enable_mineru = gr.Checkbox(
            value=True,
            label="启用 MinerU（图片型 PDF）",
            info="使用 MinerU 处理图片型 PDF，失败则自动降级"
        )

    # 进度显示
    progress_text = gr.Textbox(
        label="🔄 转换进度",
        value="等待上传文件...",
        interactive=False
    )

    # 转换按钮
    convert_btn = gr.Button("🚀 开始转换", variant="primary", size="lg")

    # 结果下载
    output_files = gr.File(
        label="✅ 转换结果",
        file_count="multiple"
    )

    # 处理报告
    report_text = gr.Textbox(
        label="📊 处理报告",
        interactive=False,
        lines=10
    )

    # 绑定事件
    convert_btn.click(
        fn=convert_files,
        inputs=[file_input, timeout_slider, enable_mineru],
        outputs=[output_files, progress_text, report_text]
    )

    # 使用说明
    with gr.Accordion("📖 使用说明", open=False):
        gr.Markdown(
            """
            ### 支持的文件格式
            - **PDF**: 文本型和图片型 PDF
            - **Word**: .docx 格式
            - **Excel**: .xlsx 和 .xls 格式

            ### 功能特点
            - 🎯 智能检测 PDF 类型，自动选择最佳转换方案
            - 🚀 图片型 PDF 使用 MinerU OCR 技术
            - ⏱️ 超时自动降级，确保转换成功
            - 📦 批量处理，支持一次转换多个文件

            ### 输出说明
            - 转换后的 Markdown 文件保存在原文件同目录
            - 图片保存在原文件同目录的 `assets/images` 文件夹

            ### 注意事项
            - 图片型 PDF 转换可能需要较长时间，请耐心等待
            - 如遇超时，系统会自动降级到备选方案
            """
        )


if __name__ == "__main__":
    # 启动应用
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
```

- [ ] **步骤 2：测试应用启动**

```bash
python app.py
```

预期：应用启动成功，浏览器访问 http://localhost:7860 可以看到界面

- [ ] **步骤 3：Commit**

```bash
git add app.py
git commit -m "feat: 添加 Gradio 主应用"
```

---

## 任务 12：测试和验证

**文件：**
- 无新文件，运行所有测试

- [ ] **步骤 1：运行所有单元测试**

```bash
pytest tests/ -v --tb=short
```

预期：所有测试通过

- [ ] **步骤 2：运行集成测试（手动）**

按照测试清单手动测试：

```
□ 启动应用
    python app.py
    访问 http://localhost:7860

□ 上传测试文件
    - 上传 tests/fixtures/sample_text.pdf
    - 检查转换结果

□ 检查输出
    - 验证 Markdown 文件生成
    - 验证格式是否正确
```

- [ ] **步骤 3：修复发现的问题**

如果测试发现问题，修复并重新测试。

- [ ] **步骤 4：最终 Commit**

```bash
git add .
git commit -m "test: 完成所有测试验证"
```

---

## 任务 13：文档和清理

**文件：**
- 创建：`README.md`
- 创建：`logs/.gitkeep`

- [ ] **步骤 1：创建 README**

```markdown
# Bruce Wu 的转化小站

文档格式转换工具 - 支持 PDF、Word、Excel 转 Markdown

## 功能特点

- 🎯 智能检测 PDF 类型（文本型/图片型）
- 🚀 图片型 PDF 使用 MinerU OCR 技术
- ⏱️ 超时自动降级机制
- 📦 批量处理支持
- 🎨 现代化 Web 界面，支持拖拽上传

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动应用

```bash
python app.py
```

### 3. 访问界面

浏览器打开 http://localhost:7860

## 支持的格式

| 格式 | 扩展名 | 说明 |
|------|--------|------|
| PDF | .pdf | 文本型和图片型 PDF |
| Word | .docx | Microsoft Word 文档 |
| Excel | .xlsx, .xls | Microsoft Excel 表格 |

## 输出说明

- 转换后的 Markdown 文件保存在原文件同目录
- 图片保存在原文件同目录的 `assets/images` 文件夹

## 项目结构

```
.
├── app.py                 # 主程序入口
├── requirements.txt       # 项目依赖
├── converters/           # 转换器模块
│   ├── pdf_converter.py
│   ├── word_converter.py
│   └── excel_converter.py
├── utils/                # 工具模块
│   ├── timeout_handler.py
│   ├── image_handler.py
│   └── file_detector.py
└── tests/                # 测试文件
```

## 许可证

MIT License
```

- [ ] **步骤 2：创建 .gitignore**

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
logs/*.log

# OS
.DS_Store
Thumbs.db

# Test files
tests/fixtures/*.pdf
tests/fixtures/*.docx
tests/fixtures/*.xlsx
```

- [ ] **步骤 3：最终 Commit**

```bash
git add README.md .gitignore logs/.gitkeep
git commit -m "docs: 添加项目文档和配置文件"
```

---

## 执行完成检查清单

完成所有任务后，确认以下内容：

- [ ] 所有单元测试通过
- [ ] 应用可以正常启动
- [ ] Web 界面可以正常访问
- [ ] PDF 转换功能正常
- [ ] Word 转换功能正常
- [ ] Excel 转换功能正常
- [ ] 批量处理功能正常
- [ ] 超时降级机制正常
- [ ] 所有代码已提交到 Git

---

**计划版本**: 1.0
**创建日期**: 2026-06-14
