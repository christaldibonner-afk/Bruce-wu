#!/usr/bin/env python3
"""
YAML Front Matter 添加脚本
为婚外情无效赠予数据集添加标准化元信息
"""

import os
import re
from pathlib import Path
from datetime import datetime

PROCESSED_DIR = Path.home() / "Desktop" / "legal-data-homework" / "01_processed"

def extract_title(content):
    """提取标题"""
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    return match.group(1).strip() if match else "未命名文件"

def get_category(filename):
    """判断文件类别"""
    if filename.startswith('law_'):
        return '法规'
    elif filename.startswith('case_'):
        return '案例'
    elif filename.startswith('article_'):
        return '实务文章'
    return '其他'

def get_tags(content, category):
    """提取标签"""
    tags = ['婚外情无效赠予']
    if category == '法规':
        if '民法典' in content:
            tags.append('民法典')
        if '公序良俗' in content:
            tags.append('公序良俗')
        if '夫妻共同财产' in content:
            tags.append('夫妻共同财产')
        if '赠予' in content:
            tags.append('赠予合同')
    elif category == '案例':
        if '一审' in content:
            tags.append('一审')
        if '二审' in content:
            tags.append('二审')
        if '返还财产' in content:
            tags.append('财产返还')
        if '房产' in content:
            tags.append('房产赠予')
    return tags

def get_case_info(content):
    """提取案例信息"""
    info = {}
    patterns = {
        'court': r'\*\*法院\*\*:\s*(.+)',
        'case_number': r'\*\*案号\*\*:\s*(.+)',
        'judgment_date': r'\*\*裁判日期\*\*:\s*(.+)',
        'case_type': r'\*\*案由\*\*:\s*(.+)',
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, content)
        if match:
            info[key] = match.group(1).strip()
    return info

def get_law_info(content):
    """提取法规信息"""
    info = {}
    patterns = {
        'department': r'\*\*发布机关\*\*:\s*(.+)',
        'law_type': r'\*\*文件类型\*\*:\s*(.+)',
        'status': r'\*\*状态\*\*:\s*(.+)',
        'publish_date': r'\*\*发布日期\*\*:\s*(.+)',
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, content)
        if match:
            info[key] = match.group(1).strip()
    return info

def generate_yaml(filename, content):
    """生成YAML Front Matter"""
    title = extract_title(content)
    category = get_category(filename)
    tags = get_tags(content, category)

    lines = ['---']
    lines.append(f'title: "{title}"')
    lines.append(f'category: {category}')
    lines.append(f'theme: 婚外情无效赠予')
    lines.append(f'collection_date: {datetime.now().strftime("%Y-%m-%d")}')
    lines.append(f'dataset_version: v1.0')

    # 来源
    if '模拟案例' in content:
        lines.append('source: 模拟数据（用于展示脱敏处理）')
        lines.append('source_type: 模拟创建')
    elif '国家法律法规数据库' in content:
        lines.append('source: 国家法律法规数据库')
        lines.append('source_url: https://flk.npc.gov.cn')
        lines.append('source_type: 手动整理')
    elif '最高人民法院' in content:
        lines.append('source: 最高人民法院官网')
        lines.append('source_type: 手动整理')
    else:
        lines.append('source: 法律实务资料')
        lines.append('source_type: 手动整理')

    # 标签
    lines.append('tags:')
    for tag in tags:
        lines.append(f'  - {tag}')

    # 类别特定信息
    if category == '案例' and get_case_info(content):
        lines.append('case_info:')
        for k, v in get_case_info(content).items():
            lines.append(f'  {k}: "{v}"')
        lines.append('desensitized: true')
        lines.append('desensitize_fields: [姓名, 身份证号, 手机号, 地址]')
    elif category == '法规' and get_law_info(content):
        lines.append('law_info:')
        for k, v in get_law_info(content).items():
            lines.append(f'  {k}: "{v}"')
        lines.append('desensitized: false')
        lines.append('desensitize_note: 法规文本不包含需要脱敏的主体信息')

    lines.append('---')
    lines.append('')
    return '\n'.join(lines)

def process_files():
    """批量添加YAML"""
    count = 0
    for file in PROCESSED_DIR.glob("*.md"):
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()

        if content.startswith('---'):
            print(f"跳过: {file.name}（已有YAML）")
            continue

        yaml = generate_yaml(file.name, content)
        new_content = yaml + content

        with open(file, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print(f"已处理: {file.name}")
        count += 1

    print(f"\nYAML添加完成！共处理 {count} 个文件")

if __name__ == "__main__":
    process_files()