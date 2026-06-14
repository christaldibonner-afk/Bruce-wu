# 文档格式转换工具设计规格

**版本**: 1.0
**日期**: 2026-06-14
**作者**: Claude

---

## 1. 项目概述

### 1.1 目标

创建一个 Web 应用工具，将 PDF、Word、Excel 文档转换为 Markdown 格式，支持：
- 文本型和图片型 PDF 的智能处理
- 格式保留（标题、表格、代码块、图片）
- 拖拽上传界面
- 超时自动降级机制

### 1.2 核心需求

| 需求项 | 详细说明 |
|-------|---------|
| **支持格式** | PDF、Word (.docx)、Excel (.xlsx/.xls) |
| **格式保留** | 标题层级结构、表格格式、代码块和引用、图片提取 |
| **使用场景** | 单个文件转换 + 批量转换 |
| **界面类型** | Web 网页界面，支持拖拽上传 |
| **输出位置** | 原文件同目录 |
| **图片存储** | 在 Markdown 同级创建 assets/images 文件夹 |
| **超时处理** | 5 分钟超时后自动降级 |
| **MinerU** | 已安装，用于图片型 PDF 处理 |

---

## 2. 技术架构

### 2.1 技术栈选择

**方案**: Python + Gradio 快速方案

**技术栈**:
- **界面框架**: Gradio 4.x
- **PDF 处理**:
  - pdfplumber - 文本型 PDF 提取
  - magic-pdf (MinerU) - 图片型 PDF OCR
  - pymupdf - 备选方案
- **Word 处理**: mammoth + python-docx
- **Excel 处理**: pandas + openpyxl
- **并发控制**: multiprocessing

### 2.2 项目结构

```
项目根目录/
├── app.py                      # Gradio 主程序入口
├── requirements.txt            # Python 依赖
├── converters/                 # 转换器模块
│   ├── __init__.py
│   ├── pdf_converter.py       # PDF 转换器
│   ├── word_converter.py      # Word 转换器
│   ├── excel_converter.py     # Excel 转换器
│   └── base_converter.py      # 基类和通用工具
├── utils/                      # 工具模块
│   ├── __init__.py
│   ├── timeout_handler.py     # 超时处理
│   ├── image_handler.py       # 图片处理
│   └── file_detector.py       # 文件类型检测
└── tests/                      # 测试文件
    ├── test_converters.py
    └── fixtures/              # 测试数据
```

---

## 3. 核心模块设计

### 3.1 PDF 转换器（pdf_converter.py）

**职责**: 处理 PDF 文件转换为 Markdown

**核心逻辑**:

```
PDF 转换流程：
1. 检测 PDF 类型（文本型 vs 图片型）
   - 提取第一页，检测文字密度
   - 文字密度 < 10% → 图片型 PDF
   - 文字密度 >= 10% → 文本型 PDF

2. 根据类型选择转换方案：
   文本型 PDF：
   └─ pdfplumber.extract_text() → 清理格式 → Markdown

   图片型 PDF：
   └─ 尝试 MinerU (magic-pdf)
      ├─ 成功 → 返回结果
      └─ 超时/失败 → 降级到 pymupdf + OCR

3. 提取图片：
   - 使用 pdfplumber 提取嵌入图片
   - 保存到 assets/images 文件夹
   - 在 Markdown 中引用图片路径
```

**关键方法**:
- `detect_pdf_type()` - 检测 PDF 类型
- `convert_text_pdf()` - 处理文本型 PDF
- `convert_image_pdf()` - 处理图片型 PDF（MinerU）
- `convert_with_fallback()` - 带降级的转换
- `extract_images()` - 提取图片

### 3.2 Word 转换器（word_converter.py）

**职责**: 处理 .docx 文件转换为 Markdown

**核心逻辑**:

```
Word 转换流程：
1. 使用 mammoth 转换主体内容
   - mammoth.extract_raw_text() → Markdown

2. 使用 python-docx 补充细节
   - 提取标题层级
   - 处理表格结构
   - 提取图片

3. 格式整理：
   - 合并标题和内容
   - 处理表格语法
   - 整理图片引用
```

**关键方法**:
- `convert_to_markdown()` - 主转换方法
- `process_tables()` - 处理表格
- `process_images()` - 提取图片

### 3.3 Excel 转换器（excel_converter.py）

**职责**: 处理 .xlsx/.xls 文件转换为 Markdown

**核心逻辑**:

```
Excel 转换流程：
1. 使用 pandas 读取 Excel
   - pd.read_excel() → DataFrame

2. 处理多个工作表：
   - 每个工作表转换为独立章节
   - 工作表名称作为二级标题

3. 表格转换：
   - df.to_markdown() → Markdown 表格
   - 处理合并单元格（拆分为独立单元格）
   - 处理空值（替换为空字符串）
```

**关键方法**:
- `convert_to_markdown()` - 主转换方法
- `process_sheet()` - 处理单个工作表
- `handle_merged_cells()` - 处理合并单元格

---

## 4. 文件处理流程

### 4.1 单个文件处理流程

```
用户上传文件
    ↓
检测文件类型 (通过扩展名)
    ↓
    ├─ .pdf  → PDF 转换器
    ├─ .docx → Word 转换器
    ├─ .xlsx → Excel 转换器
    └─ .xls  → Excel 转换器
    ↓
启动超时监控 (5分钟)
    ↓
执行转换
    ↓
    ├─ 成功 → 保存 Markdown 文件
    │         ↓
    │    提取图片 (如有)
    │         ↓
    │    保存到 assets/images
    │         ↓
    │    返回结果文件
    │
    └─ 失败/超时 → 尝试降级方案
                   ↓
              ├─ 成功 → 返回结果
              └─ 失败 → 返回错误信息
```

### 4.2 批量文件处理流程

```
用户上传多个文件
    ↓
创建任务队列
    ↓
并发处理 (最大并发数：3)
    ↓
每个文件独立执行上述流程
    ↓
    ├─ 成功 → 加入成功列表
    └─ 失败 → 加入失败列表
    ↓
生成处理报告
    - 成功文件数
    - 失败文件数
    - 失败原因
    ↓
打包所有成功文件
    ↓
提供下载
```

### 4.3 图片处理流程

```
检测文档中的图片
    ↓
    ├─ PDF: 使用 pdfplumber 提取嵌入图片
    ├─ Word: 使用 python-docx 提取图片
    └─ Excel: 截取图表区域 (如有)
    ↓
创建图片存储目录
    ├─ 位置: 原文件同目录/assets/images
    └─ 命名: {原文件名}_img_{序号}.{扩展名}
    ↓
保存图片
    ↓
在 Markdown 中插入引用
    格式: ![描述](./assets/images/图片名.png)
```

---

## 5. 超时和降级机制

### 5.1 超时控制实现

**实现方案**: 使用 `multiprocessing.Process` + `join(timeout=300)`

```python
from multiprocessing import Process, Queue

def convert_with_timeout(file_path, timeout=300):
    """带超时的转换函数"""
    result_queue = Queue()

    # 创建子进程执行转换
    process = Process(
        target=convert_file,
        args=(file_path, result_queue)
    )
    process.start()

    # 等待结果，最多等 5 分钟
    process.join(timeout=timeout)

    if process.is_alive():
        # 超时，强制终止
        process.terminate()
        process.join()
        return None  # 触发降级
    else:
        # 成功完成
        return result_queue.get()
```

### 5.2 降级策略矩阵

| 文件类型 | 主方案 | 降级方案 | 降级触发条件 |
|---------|--------|---------|-------------|
| **文本型 PDF** | pdfplumber | pymupdf | pdfplumber 失败/超时 |
| **图片型 PDF** | MinerU (magic-pdf) | pymupdf + pdfplumber | MinerU 超时/失败/未安装 |
| **Word** | mammoth | python-docx | mammoth 失败/超时 |
| **Excel** | pandas + to_markdown | openpyxl + 手动构建 | pandas 失败/超时 |

### 5.3 超时时间配置

```python
TIMEOUT_CONFIG = {
    'pdf_text': 180,           # 文本型 PDF：3 分钟
    'pdf_image': 300,          # 图片型 PDF：5 分钟
    'pdf_image_mineru': 300,   # MinerU：5 分钟
    'word': 120,               # Word：2 分钟
    'excel': 120,              # Excel：2 分钟
}
```

### 5.4 用户反馈机制

在界面上实时显示：
- 当前处理阶段
- 已用时间
- 使用的转换方案（主方案/降级方案）
- 如果降级，显示降级原因

---

## 6. 界面设计

### 6.1 整体布局

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│           🎉 Bruce Wu 的转化小站 🎉                     │
│                                                         │
│         支持 PDF、Word、Excel 转 Markdown               │
│                                                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  📁 文件上传区（支持拖拽）                                │
│  ┌───────────────────────────────────────────────────┐  │
│  │                                                   │  │
│  │         将文件拖拽到此处，或点击上传               │  │
│  │                                                   │  │
│  │         支持：.pdf, .docx, .xlsx, .xls           │  │
│  │         可同时上传多个文件                        │  │
│  │                                                   │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  ⚙️ 转换设置（可选）                                     │
│  ┌──────────────────────┬───────────────────────────┐  │
│  │ 图片处理方式:        │ ☑ 提取并保存为文件         │  │
│  ├──────────────────────┼───────────────────────────┤  │
│  │ 超时时间:            │ [  300  ] 秒 (图片型PDF)  │  │
│  ├──────────────────────┼───────────────────────────┤  │
│  │ 启用 MinerU:         │ ☑ 自动检测并使用          │  │
│  └──────────────────────┴───────────────────────────┘  │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  🔄 转换进度                                             │
│  ┌───────────────────────────────────────────────────┐  │
│  │ 文件 1/3: example.pdf                             │  │
│  │ ████████████░░░░░░░░ 60%                         │  │
│  │ 状态: 使用 MinerU 处理图片型 PDF...               │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  ✅ 转换结果                                             │
│  ┌───────────────────────────────────────────────────┐  │
│  │ 📄 example.md           [下载]                    │  │
│  │ 📦 example_assets.zip   [下载] (包含图片)         │  │
│  │                                                   │  │
│  │ 批量下载: [下载所有文件]                          │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  📊 处理报告                                             │
│  ┌───────────────────────────────────────────────────┐  │
│  │ 总计: 3 个文件                                    │  │
│  │ ✅ 成功: 2 个                                     │  │
│  │ ❌ 失败: 1 个                                     │  │
│  │                                                   │  │
│  │ 失败文件:                                         │  │
│  │ - document2.pdf: MinerU 超时，降级方案失败       │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 6.2 Gradio 组件实现

```python
import gradio as gr

with gr.Blocks(title="Bruce Wu 的转化小站") as app:
    # 抬头
    gr.Markdown(
        """
        # 🎉 Bruce Wu 的转化小站 🎉

        支持 PDF、Word、Excel 转 Markdown
        """
    )

    # 文件上传组件
    file_input = gr.File(
        label="📁 文件上传",
        file_count="multiple",
        file_types=[".pdf", ".docx", ".xlsx", ".xls"]
    )

    # 设置区域
    with gr.Accordion("⚙️ 高级设置", open=False):
        timeout_slider = gr.Slider(
            minimum=60, maximum=600, value=300,
            label="超时时间（秒）"
        )
        enable_mineru = gr.Checkbox(
            value=True, label="启用 MinerU（图片型 PDF）"
        )

    # 进度显示
    progress_text = gr.Textbox(
        label="🔄 转换进度",
        interactive=False
    )

    # 转换按钮
    convert_btn = gr.Button("开始转换", variant="primary")

    # 结果下载
    output_files = gr.File(
        label="✅ 转换结果",
        file_count="multiple"
    )

    # 处理报告
    report_text = gr.Textbox(
        label="📊 处理报告",
        interactive=False
    )

    # 绑定事件
    convert_btn.click(
        fn=convert_files,
        inputs=[file_input, timeout_slider, enable_mineru],
        outputs=[output_files, progress_text, report_text]
    )
```

---

## 7. 错误处理机制

### 7.1 错误类型分类

| 错误类型 | 触发场景 | 处理策略 | 用户提示 |
|---------|---------|---------|---------|
| **文件格式错误** | 不支持的文件类型 | 拒绝处理 | "不支持的文件格式，请上传 PDF/Word/Excel 文件" |
| **文件损坏** | 无法读取文件 | 尝试修复或跳过 | "文件可能已损坏，无法读取" |
| **转换失败** | 转换过程出错 | 尝试降级方案 | "主方案失败，正在尝试备选方案..." |
| **超时** | 处理时间过长 | 强制终止并降级 | "处理超时，正在切换备选方案..." |
| **内存不足** | 文件过大 | 清理缓存并重试 | "文件较大，正在优化处理..." |
| **权限错误** | 无法写入文件 | 提示用户检查 | "无法保存文件，请检查目录权限" |
| **MinerU 错误** | MinerU 未安装/失败 | 自动降级 | "MinerU 不可用，使用备选方案" |

### 7.2 错误处理流程

```
捕获异常
    ↓
记录错误日志
    ├─ 错误类型
    ├─ 错误消息
    ├─ 文件信息
    └─ 时间戳
    ↓
判断错误类型
    ├─ 可恢复错误 → 尝试降级方案
    │   ├─ 降级成功 → 继续处理
    │   └─ 降级失败 → 标记为失败
    │
    └─ 不可恢复错误 → 直接标记为失败
    ↓
生成错误报告
    ├─ 失败文件列表
    ├─ 失败原因
    └─ 建议解决方案
    ↓
展示给用户
```

### 7.3 异常捕获代码

```python
class ConversionError(Exception):
    """转换错误基类"""
    pass

class TimeoutError(ConversionError):
    """超时错误"""
    pass

class FallbackError(ConversionError):
    """降级失败错误"""
    pass

def safe_convert(file_path, converter):
    """安全的转换函数"""
    try:
        result = converter.convert(file_path)
        return {'success': True, 'data': result}

    except TimeoutError:
        logger.warning(f"转换超时: {file_path}")
        try:
            result = converter.fallback_convert(file_path)
            return {'success': True, 'data': result, 'used_fallback': True}
        except Exception as e:
            return {'success': False, 'error': f"降级失败: {str(e)}"}

    except ConversionError as e:
        logger.error(f"转换失败: {file_path} - {str(e)}")
        return {'success': False, 'error': str(e)}

    except Exception as e:
        logger.exception(f"未知错误: {file_path}")
        return {'success': False, 'error': f"未知错误: {str(e)}"}
```

### 7.4 日志记录

**日志文件位置**: `./logs/conversion.log`

**日志格式**:
```
[2024-06-14 10:30:15] INFO - 开始转换: example.pdf
[2024-06-14 10:30:16] INFO - 检测为图片型 PDF
[2024-06-14 10:30:17] INFO - 使用 MinerU 处理
[2024-06-14 10:32:20] WARNING - MinerU 超时 (120秒)
[2024-06-14 10:32:21] INFO - 降级到 pymupdf
[2024-06-14 10:33:00] INFO - 转换成功: example.md
```

---

## 8. 测试方案

### 8.1 测试策略

采用**单元测试 + 集成测试 + 手动测试**的三层测试策略。

### 8.2 单元测试

**测试文件**: `tests/test_converters.py`

**测试覆盖**:

```python
# PDF 转换器测试
test_detect_pdf_type()
    ├─ 测试文本型 PDF 检测
    ├─ 测试图片型 PDF 检测
    └─ 测试混合型 PDF 检测

test_convert_text_pdf()
    ├─ 测试标题提取
    ├─ 测试表格转换
    ├─ 测试代码块识别
    └─ 测试图片提取

test_convert_image_pdf()
    ├─ 测试 MinerU 调用
    ├─ 测试降级机制
    └─ 测试超时处理

# Word 转换器测试
test_convert_word()
    ├─ 测试标题层级
    ├─ 测试表格转换
    └─ 测试图片提取

# Excel 转换器测试
test_convert_excel()
    ├─ 测试单工作表
    ├─ 测试多工作表
    └─ 测试合并单元格
```

### 8.3 集成测试

**测试文件**: `tests/test_integration.py`

**测试场景**:

| 测试场景 | 测试文件 | 预期结果 |
|---------|---------|---------|
| 文本型 PDF 转换 | sample_text.pdf | 准确提取文本、表格、图片 |
| 图片型 PDF 转换 | sample_image.pdf | MinerU OCR 识别成功 |
| 图片型 PDF 超时 | large_image.pdf | 5分钟超时后自动降级 |
| Word 文档转换 | sample.docx | 保留格式、提取图片 |
| Excel 表格转换 | sample.xlsx | 正确转换多个工作表 |
| 批量文件转换 | 混合文件 | 全部成功或生成失败报告 |

### 8.4 手动测试清单

```
□ 1. 启动应用
    - 运行 python app.py
    - 浏览器访问 http://localhost:7860
    - 检查界面显示是否正常

□ 2. 文件上传测试
    - 拖拽单个文件上传
    - 拖拽多个文件上传
    - 点击按钮选择文件
    - 上传不支持的格式（应被拒绝）

□ 3. PDF 转换测试
    - 上传普通文本型 PDF
    - 检查转换后的 Markdown 格式
    - 检查图片是否正确提取
    - 上传图片型 PDF
    - 观察 MinerU 是否被调用
    - 检查转换结果

□ 4. Word/Excel 转换测试
    - 上传 Word 文档
    - 检查格式保留情况
    - 上传 Excel 文件
    - 检查表格转换结果

□ 5. 超时测试
    - 上传大型图片型 PDF
    - 观察是否在 5 分钟后降级
    - 检查降级后的转换结果

□ 6. 错误处理测试
    - 上传损坏的文件
    - 检查错误提示是否清晰
    - 检查日志记录是否完整

□ 7. 批量转换测试
    - 上传 5 个不同类型文件
    - 检查并发处理情况
    - 检查结果打包下载
```

### 8.5 性能基准

**预期性能指标**:

| 文件类型 | 文件大小 | 预期转换时间 | 备注 |
|---------|---------|-------------|------|
| 文本型 PDF | < 5MB | < 10 秒 | pdfplumber |
| 文本型 PDF | 5-20MB | 10-30 秒 | pdfplumber |
| 图片型 PDF | < 5MB | 30-120 秒 | MinerU |
| 图片型 PDF | 5-20MB | 120-300 秒 | MinerU |
| Word 文档 | < 10MB | < 5 秒 | mammoth |
| Excel 表格 | < 5MB | < 5 秒 | pandas |

### 8.6 测试数据

**测试文件准备**:
- `tests/fixtures/sample_text.pdf` - 文本型 PDF
- `tests/fixtures/sample_image.pdf` - 图片型 PDF
- `tests/fixtures/sample.docx` - Word 文档
- `tests/fixtures/sample.xlsx` - Excel 表格
- `tests/fixtures/large_image.pdf` - 大型图片型 PDF（用于超时测试）
- `tests/fixtures/corrupted.pdf` - 损坏的 PDF（用于错误测试）

---

## 9. 部署说明

### 9.1 环境要求

- Python 3.8+
- 操作系统：Windows / macOS / Linux
- 内存：建议 4GB+（处理大型 PDF）

### 9.2 依赖安装

```bash
pip install -r requirements.txt
```

**requirements.txt**:
```
gradio>=4.0.0
pdfplumber>=0.10.0
pymupdf>=1.23.0
mammoth>=1.6.0
python-docx>=1.1.0
pandas>=2.0.0
openpyxl>=3.1.0
Pillow>=10.0.0
magic-pdf[full]>=0.6.0  # MinerU
```

### 9.3 启动命令

```bash
python app.py
```

访问地址：`http://localhost:7860`

---

## 10. 后续优化方向

1. **性能优化**
   - 添加文件预处理缓存
   - 优化大文件分块处理
   - 支持断点续传

2. **功能扩展**
   - 支持更多格式（PPT、RTF、TXT）
   - 添加批量处理历史记录
   - 支持自定义 Markdown 模板

3. **部署优化**
   - Docker 容器化部署
   - 云端部署支持
   - API 接口开放

---

**文档版本历史**:
- v1.0 (2026-06-14): 初始版本
