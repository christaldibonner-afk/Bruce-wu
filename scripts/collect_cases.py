#!/usr/bin/env python3
"""
裁判文书网案例采集脚本
使用OpenCLI browser命令自动化采集劳动争议相关案例
"""

import subprocess
import json
import re
import os
import time

RAW_DIR = os.path.expanduser("~/Desktop/legal-data-homework/00_raw")

def run_opencli(cmd):
    """执行opencli命令并返回结果"""
    result = subprocess.run(
        f"opencli browser wenshu {cmd}",
        shell=True,
        capture_output=True,
        text=True,
        timeout=60
    )
    return result.stdout

def extract_page_content():
    """提取当前页面的文本内容"""
    output = run_opencli("extract")
    # 解析JSON输出
    try:
        # 找到JSON部分
        json_match = re.search(r'\{.*\}', output, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            return data.get("content", "")
    except:
        pass
    return output

def save_case(content, filename):
    """保存案例内容到文件"""
    filepath = os.path.join(RAW_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"已保存: {filepath}")

def parse_case_list(content):
    """从页面内容中解析案例列表"""
    cases = []

    # 提取案例标题和基本信息
    pattern = r'\[([^\]]+)\].*?href=([^>]+)>.*?([^<]+)</a>\s*\n([^\[]+)\n####\s*\[裁判理由\]\s*\n([^\[]+)'

    matches = re.findall(pattern, content, re.DOTALL)

    for match in matches:
        case = {
            "index": match[0],
            "url": match[1],
            "title": match[2].strip(),
            "court_info": match[3].strip(),
            "reason": match[4].strip()[:500]  # 截取前500字
        }
        cases.append(case)

    return cases

def main():
    """主函数"""
    print("开始采集案例...")

    # 提取当前页面内容
    content = extract_page_content()

    # 解析案例列表
    cases = parse_case_list(content)

    print(f"发现 {len(cases)} 个案例")

    # 保存每个案例
    for i, case in enumerate(cases):
        filename = f"case_{i+1:03d}.md"
        case_content = f"""# {case['title']}

**法院信息**: {case['court_info']}

## 裁判理由摘要

{case['reason']}

---
*采集时间: {time.strftime('%Y-%m-%d %H:%M:%S')}*
*来源: 中国裁判文书网*
"""
        save_case(case_content, filename)

    print("采集完成!")

if __name__ == "__main__":
    main()