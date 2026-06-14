# Bruce Wu 的转化小站 🎉

> 一个简洁高效的文档格式转换工具，支持 PDF、Word、Excel 转换为 Markdown 格式

## ✨ 功能特点

- 🎯 **智能检测** - 自动识别 PDF 类型（文本型/图片型），选择最佳转换方案
- 🚀 **OCR 支持** - 图片型 PDF 使用 MinerU OCR 技术，提取图片中的文字
- ⏱️ **超时保护** - 5 分钟超时自动降级机制，确保转换成功
- 📦 **批量处理** - 支持一次上传多个文件，批量转换
- 🎨 **现代界面** - 基于 Gradio 的 Web 界面，支持拖拽上传
- 📊 **进度显示** - 实时显示转换进度和处理报告

## 🚀 快速开始

### 环境要求

- Python 3.8+
- 操作系统：Windows / macOS / Linux

### 安装步骤

**1. 克隆仓库**

```bash
git clone https://github.com/your-username/document-converter.git
cd document-converter
```

**2. 创建虚拟环境（推荐）**

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows
```

**3. 安装依赖**

```bash
pip install -r requirements.txt
```

### 启动应用

```bash
python app.py
```

应用启动后，浏览器访问：**http://localhost:7860**

## 📋 支持的格式

| 格式 | 扩展名 | 说明 | 转换方式 |
|------|--------|------|---------|
| PDF | .pdf | 文本型 PDF | pdfplumber 提取文本和表格 |
| PDF | .pdf | 图片型 PDF | MinerU OCR / pymupdf 降级 |
| Word | .docx | Microsoft Word | mammoth + python-docx |
| Excel | .xlsx, .xls | Microsoft Excel | pandas 转 Markdown 表格 |

## 💡 使用说明

### Web 界面使用

1. **上传文件** - 拖拽文件到上传区域，或点击选择文件
2. **配置设置**（可选）- 调整超时时间、启用/禁用 MinerU
3. **开始转换** - 点击"开始转换"按钮
4. **下载结果** - 转换完成后下载 Markdown 文件

### 命令行使用

```python
from converters import PDFConverter, WordConverter, ExcelConverter

# PDF 转换
pdf_converter = PDFConverter()
markdown = pdf_converter.convert("document.pdf")

# Word 转换
word_converter = WordConverter()
markdown = word_converter.convert("document.docx")

# Excel 转换
excel_converter = ExcelConverter()
markdown = excel_converter.convert("spreadsheet.xlsx")
```

## 📁 项目结构

```
document-converter/
├── app.py                      # Gradio Web 应用主程序
├── requirements.txt            # Python 依赖列表
├── README.md                   # 项目文档
├── .gitignore                  # Git 忽略配置
├── converters/                 # 转换器模块
│   ├── __init__.py
│   ├── base_converter.py      # 转换器基类
│   ├── pdf_converter.py       # PDF 转 Markdown
│   ├── word_converter.py      # Word 转 Markdown
│   └── excel_converter.py     # Excel 转 Markdown
├── utils/                      # 工具模块
│   ├── __init__.py
│   ├── file_detector.py       # 文件类型检测
│   ├── image_handler.py       # 图片处理工具
│   └── timeout_handler.py     # 超时处理工具
└── tests/                      # 单元测试
    ├── test_pdf_converter.py
    ├── test_word_converter.py
    └── test_excel_converter.py
```

## 🔧 技术栈

- **Web 框架**: Gradio 4.x - 快速构建 ML 应用界面
- **PDF 处理**:
  - pdfplumber - 文本型 PDF 提取
  - pymupdf - PDF 备选方案
  - MinerU (magic-pdf) - 图片型 PDF OCR
- **Word 处理**:
  - mammoth - Word 转 Markdown
  - python-docx - Word 文档解析
- **Excel 处理**:
  - pandas - 数据处理
  - openpyxl - Excel 文件读取
  - tabulate - 表格格式化
- **图片处理**: Pillow
- **并发控制**: threading (超时处理)

## ⚙️ 配置说明

### 超时设置

默认超时时间为 300 秒（5 分钟），可在界面中调整（60-600 秒）。

### MinerU 配置

MinerU 用于处理图片型 PDF（扫描件）。如果未安装，系统会自动降级到 pymupdf。

安装 MinerU（可选）：
```bash
pip install magic-pdf[full]
```

## 📊 性能参考

| 文件类型 | 文件大小 | 预期转换时间 | 备注 |
|---------|---------|-------------|------|
| 文本型 PDF | < 5MB | < 10 秒 | pdfplumber |
| 文本型 PDF | 5-20MB | 10-30 秒 | pdfplumber |
| 图片型 PDF | < 5MB | 30-120 秒 | MinerU OCR |
| 图片型 PDF | 5-20MB | 120-300 秒 | MinerU OCR |
| Word 文档 | < 10MB | < 5 秒 | mammoth |
| Excel 表格 | < 5MB | < 5 秒 | pandas |

## 🐛 常见问题

### 1. 安装依赖失败？

建议使用虚拟环境：
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. MinerU 安装失败？

MinerU 是可选依赖，安装失败不影响文本型 PDF 转换。系统会自动降级。

### 3. 转换超时怎么办？

- 增加"超时时间"设置
- 图片型 PDF 会自动降级到 pymupdf
- 检查文件是否过大或损坏

### 4. 中文显示乱码？

确保文件使用 UTF-8 编码，Markdown 文件保存时使用 UTF-8 编码。

## 📝 输出说明

- **Markdown 文件**：保存在原文件同目录，文件名相同，扩展名为 `.md`
- **图片文件**：保存在原文件同目录的 `assets/images/` 文件夹
- **图片命名**：`{原文件名}_img_{序号}.{扩展名}`

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 👤 作者

**Bruce Wu**

## 🙏 致谢

- [Gradio](https://gradio.app/) - 优秀的 ML 应用框架
- [pdfplumber](https://github.com/jsvine/pdfplumber) - PDF 文本提取
- [MinerU](https://github.com/opendatalab/MinerU) - PDF OCR 解决方案
- [mammoth](https://github.com/mwilliamson/python-mammoth) - Word 转换工具
- [pandas](https://pandas.pydata.org/) - 数据处理库
