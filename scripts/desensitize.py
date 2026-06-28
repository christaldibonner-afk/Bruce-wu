#!/usr/bin/env python3
"""
婚外情无效赠予数据脱敏处理脚本

脱敏内容：
1. 姓名：张美玲 → 张某某
2. 身份证号：18位 → ******************
3. 手机号：11位 → ***********
4. 地址：详细地址 → 某省某市某区
5. 案号：具体编号 → XXXX
"""

import os
import re
from pathlib import Path

RAW_DIR = Path.home() / "Desktop" / "legal-data-homework" / "00_raw"
PROCESSED_DIR = Path.home() / "Desktop" / "legal-data-homework" / "01_processed"

# 需要脱敏的姓名列表
NAMES_TO_DESENSITIZE = [
    # 案例1当事人
    '张美玲', '李建国', '王小红', '陈法官', '林书记',
    # 案例2当事人
    '赵丽娜', '刘雅琴', '陈志强', '王审判长', '李审判员', '张审判员', '周书记',
    # 案例3当事人
    '孙丽华', '周建华', '吴美玲', '郑法官', '陈书记',
    # 案例4当事人
    '黄淑芬', '林伟强', '郑雅婷', '杨法官', '钟书记',
    # 其他可能出现的姓名
    '张三', '李四', '王五', '赵六', '钱七', '孙八', '周九', '吴十'
]

def desensitize_name(text):
    """脱敏姓名"""
    for name in NAMES_TO_DESENSITIZE:
        if name in text:
            # 保留姓氏，替换为"某某"
            replacement = name[0] + '某某'
            text = text.replace(name, replacement)
    return text

def desensitize_id_number(text):
    """脱敏身份证号"""
    # 匹配18位身份证号
    pattern = r'\d{6}[12]\d{3}[01]\d{2}[0-3]\d{2}\d{3}[\dXx]'
    return re.sub(pattern, '******************', text)

def desensitize_phone(text):
    """脱敏手机号"""
    pattern = r'1[3-9]\d{9}'
    return re.sub(pattern, '***********', text)

def desensitize_address(text):
    """脱敏地址"""
    # 住址模式
    patterns = [
        (r'住[^，。\n]{15,60}', '住某省某市某区'),
        (r'住所地[^，。\n]{15,60}', '住所地某省某市某区'),
        (r'住浙江省杭州市[^，。\n]+', '住浙江省杭州市某区'),
        (r'住北京市[^，。\n]+', '住北京市某区'),
        (r'住广东省广州市[^，。\n]+', '住广东省广州市某区'),
        (r'住上海市[^，。\n]+', '住上海市某区'),
    ]
    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text)
    return text

def desensitize_case_number(text):
    """脱敏案号中的具体编号"""
    # 保留年份和法院代码，替换具体编号
    patterns = [
        (r'（\d{4}）([京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼]\d{2,4})[^\d]*(\d{4})号',
         r'（\g<1>）\g<2>民初XXXX号'),
        (r'（\d{4}）([京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼]\d{2,4})[^\d]*(\d{3})号',
         r'（\g<1>）\g<2>民初XXXX号'),
    ]
    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text)
    return text

def desensitize_content(content):
    """综合脱敏"""
    content = desensitize_id_number(content)
    content = desensitize_phone(content)
    content = desensitize_address(content)
    content = desensitize_name(content)
    content = desensitize_case_number(content)
    return content

def process_files():
    """批量处理文件"""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    count = 0
    for input_file in RAW_DIR.glob("*.md"):
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 脱敏处理
        processed = desensitize_content(content)

        # 保存
        output_file = PROCESSED_DIR / input_file.name
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(processed)

        print(f"已处理: {input_file.name}")
        count += 1

    print(f"\n脱敏完成！共处理 {count} 个文件")
    print(f"原始目录: {RAW_DIR}")
    print(f"处理后目录: {PROCESSED_DIR}")

if __name__ == "__main__":
    process_files()