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
with gr.Blocks(title="Bruce Wu 的转化小站") as app:

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
        show_error=True,
        theme=gr.themes.Soft()
    )
