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
