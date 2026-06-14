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
