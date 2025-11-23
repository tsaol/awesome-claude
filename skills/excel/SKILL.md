---
name: excel
description: Excel 表格创建、编辑和数据分析。支持公式、格式化、数据分析和可视化。当需要处理表格文件时使用：(1) 创建带公式的表格，(2) 读取和分析数据，(3) 修改现有表格，(4) 数据分析和可视化
---

# Excel 表格处理技能

## 概述

本技能提供完整的 Excel 表格处理能力，包括创建、编辑、数据分析和公式计算。

## 关键原则

### 使用公式而非硬编码值

**始终使用 Excel 公式，而不是在 Python 中计算后硬编码结果。** 这确保表格保持动态和可更新。

**❌ 错误示例 - 硬编码计算值：**
```python
# 错误：在 Python 中计算后硬编码
total = df['Sales'].sum()
sheet['B10'] = total  # 硬编码 5000

growth = (df.iloc[-1]['Revenue'] - df.iloc[0]['Revenue']) / df.iloc[0]['Revenue']
sheet['C5'] = growth  # 硬编码 0.15
```

**✅ 正确示例 - 使用 Excel 公式：**
```python
# 正确：使用 Excel 公式
sheet['B10'] = '=SUM(B2:B9)'
sheet['C5'] = '=(C4-C2)/C2'
sheet['D20'] = '=AVERAGE(D2:D19)'
```

## 功能特性

### 1. 数据分析（使用 pandas）

```python
import pandas as pd

# 读取 Excel
df = pd.read_excel('file.xlsx')  # 默认读取第一个工作表
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)  # 读取所有工作表

# 数据分析
df.head()      # 预览数据
df.info()      # 列信息
df.describe()  # 统计信息

# 数据操作
filtered = df[df['Sales'] > 1000]
grouped = df.groupby('Category')['Sales'].sum()

# 写入 Excel
df.to_excel('output.xlsx', index=False)
```

### 2. 创建新 Excel 文件（使用 openpyxl）

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

wb = Workbook()
sheet = wb.active
sheet.title = "销售数据"

# 添加数据
sheet['A1'] = '产品'
sheet['B1'] = '销售额'
sheet.append(['产品A', 1000])
sheet.append(['产品B', 1500])
sheet.append(['产品C', 2000])

# 添加公式
sheet['B5'] = '总计'
sheet['B6'] = '=SUM(B2:B4)'

# 格式化
sheet['A1'].font = Font(bold=True, size=14)
sheet['A1'].fill = PatternFill(start_color='FFFF00', fill_type='solid')
sheet['A1'].alignment = Alignment(horizontal='center')

# 设置列宽
sheet.column_dimensions['A'].width = 15
sheet.column_dimensions['B'].width = 12

wb.save('sales.xlsx')
```

### 3. 编辑现有 Excel 文件

```python
from openpyxl import load_workbook

# 加载文件
wb = load_workbook('existing.xlsx')
sheet = wb.active  # 或 wb['工作表名称']

# 读取数据
value = sheet['A1'].value
print(f"单元格 A1 的值: {value}")

# 修改数据
sheet['A1'] = '新值'

# 插入/删除行列
sheet.insert_rows(2)  # 在第 2 行插入
sheet.delete_cols(3)  # 删除第 3 列

# 访问多个工作表
for sheet_name in wb.sheetnames:
    sheet = wb[sheet_name]
    print(f"工作表: {sheet_name}")

# 创建新工作表
new_sheet = wb.create_sheet('新工作表')
new_sheet['A1'] = '数据'

wb.save('modified.xlsx')
```

### 4. 常用公式

```python
from openpyxl import Workbook

wb = Workbook()
sheet = wb.active

# 基础数学公式
sheet['A10'] = '=SUM(A1:A9)'           # 求和
sheet['B10'] = '=AVERAGE(B1:B9)'       # 平均值
sheet['C10'] = '=MAX(C1:C9)'           # 最大值
sheet['D10'] = '=MIN(D1:D9)'           # 最小值
sheet['E10'] = '=COUNT(E1:E9)'         # 计数

# 条件公式
sheet['F2'] = '=IF(A2>100,"高","低")'   # IF 条件
sheet['G2'] = '=SUMIF(A:A,">100",B:B)' # 条件求和
sheet['H2'] = '=COUNTIF(A:A,">100")'   # 条件计数

# 查找公式
sheet['I2'] = '=VLOOKUP(A2,A:B,2,FALSE)'  # 垂直查找

# 文本公式
sheet['J2'] = '=CONCATENATE(A2," ",B2)'   # 连接文本
sheet['K2'] = '=LEFT(A2,5)'               # 左取字符

# 日期公式
sheet['L2'] = '=TODAY()'                  # 今天日期
sheet['M2'] = '=YEAR(A2)'                 # 提取年份

wb.save('formulas.xlsx')
```

### 5. 数据格式化

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.styles.numbers import FORMAT_CURRENCY_USD, FORMAT_PERCENTAGE

wb = Workbook()
sheet = wb.active

# 字体样式
sheet['A1'].font = Font(
    name='Arial',
    size=14,
    bold=True,
    italic=False,
    color='FF0000'  # 红色
)

# 背景填充
sheet['A1'].fill = PatternFill(
    start_color='FFFF00',  # 黄色
    fill_type='solid'
)

# 对齐方式
sheet['A1'].alignment = Alignment(
    horizontal='center',  # 水平居中
    vertical='center'     # 垂直居中
)

# 边框
thin_border = Border(
    left=Side(style='thin'),
    right=Side(style='thin'),
    top=Side(style='thin'),
    bottom=Side(style='thin')
)
sheet['A1'].border = thin_border

# 数字格式
sheet['B1'] = 1234.56
sheet['B1'].number_format = FORMAT_CURRENCY_USD  # 货币格式

sheet['C1'] = 0.85
sheet['C1'].number_format = FORMAT_PERCENTAGE    # 百分比格式

sheet['D1'] = 1234.5678
sheet['D1'].number_format = '#,##0.00'           # 自定义数字格式

wb.save('formatted.xlsx')
```

### 6. 创建图表

```python
from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, PieChart, Reference

wb = Workbook()
sheet = wb.active

# 准备数据
sheet['A1'] = '月份'
sheet['B1'] = '销售额'
data = [
    ['1月', 100],
    ['2月', 120],
    ['3月', 150],
    ['4月', 180]
]
for row in data:
    sheet.append(row)

# 创建柱状图
chart = BarChart()
chart.title = "月度销售额"
chart.x_axis.title = "月份"
chart.y_axis.title = "销售额"

# 数据范围
data_ref = Reference(sheet, min_col=2, min_row=1, max_row=5)
cats_ref = Reference(sheet, min_col=1, min_row=2, max_row=5)

chart.add_data(data_ref, titles_from_data=True)
chart.set_categories(cats_ref)

# 添加图表到工作表
sheet.add_chart(chart, "D2")

wb.save('chart.xlsx')
```

### 7. 数据透视表分析

```python
import pandas as pd

# 读取数据
df = pd.read_excel('sales_data.xlsx')

# 创建数据透视表
pivot = pd.pivot_table(
    df,
    values='销售额',
    index='产品',
    columns='月份',
    aggfunc='sum',
    fill_value=0
)

# 添加合计行和列
pivot['总计'] = pivot.sum(axis=1)
pivot.loc['总计'] = pivot.sum()

# 保存到新文件
with pd.ExcelWriter('pivot_table.xlsx') as writer:
    pivot.to_excel(writer, sheet_name='数据透视表')
```

### 8. 多工作表操作

```python
from openpyxl import Workbook

wb = Workbook()

# 创建多个工作表
sheet1 = wb.active
sheet1.title = "销售数据"
sheet1['A1'] = '销售额'
sheet1['A2'] = 1000

sheet2 = wb.create_sheet("成本数据")
sheet2['A1'] = '成本'
sheet2['A2'] = 600

sheet3 = wb.create_sheet("利润分析")
sheet3['A1'] = '利润'
# 跨工作表引用公式
sheet3['A2'] = "=销售数据!A2-成本数据!A2"

wb.save('multi_sheet.xlsx')
```

## 财务模型颜色规范

创建财务模型时的行业标准颜色约定：

```python
from openpyxl.styles import Font

# 蓝色文本 - 硬编码输入值
cell.font = Font(color='0000FF')  # RGB: 0,0,255

# 黑色文本 - 公式和计算
cell.font = Font(color='000000')  # RGB: 0,0,0

# 绿色文本 - 同一工作簿内的链接
cell.font = Font(color='008000')  # RGB: 0,128,0

# 红色文本 - 外部文件链接
cell.font = Font(color='FF0000')  # RGB: 255,0,0

# 黄色背景 - 需要注意的关键假设
cell.fill = PatternFill(start_color='FFFF00', fill_type='solid')
```

## 数字格式标准

```python
# 货币格式（使用 $#,##0）
sheet['A1'].number_format = '$#,##0'

# 百分比格式（一位小数）
sheet['B1'].number_format = '0.0%'

# 将零显示为横线
sheet['C1'].number_format = '$#,##0;($#,##0);-'

# 倍数格式（如市盈率）
sheet['D1'].number_format = '0.0"x"'

# 负数使用括号
sheet['E1'].number_format = '#,##0;(#,##0)'
```

## 工作流程

1. **选择工具**：pandas 用于数据分析，openpyxl 用于公式和格式化
2. **创建/加载**：创建新工作簿或加载现有文件
3. **修改**：添加/编辑数据、公式和格式
4. **保存**：写入文件
5. **验证**：检查公式是否正确，没有错误（#REF!、#DIV/0! 等）

## 常见公式错误

- **#REF!** - 无效的单元格引用
- **#DIV/0!** - 除以零
- **#VALUE!** - 公式中数据类型错误
- **#NAME?** - 无法识别的公式名称
- **#N/A** - 值不可用

## 依赖安装

```bash
# 安装 pandas（数据分析）
pip install pandas openpyxl

# 读取 Excel 需要
pip install xlrd  # 用于旧版 .xls 格式
```

## 快速参考

| 任务 | pandas | openpyxl |
|------|--------|----------|
| 读取数据 | `pd.read_excel()` | `load_workbook()` |
| 创建工作簿 | - | `Workbook()` |
| 写入数据 | `df.to_excel()` | `sheet['A1'] = value` |
| 添加公式 | - | `sheet['A1'] = '=SUM(B:B)'` |
| 格式化 | - | `cell.font/fill/alignment` |
| 数据分析 | ✓ | - |
| 复杂格式 | - | ✓ |

## 最佳实践

1. **使用公式**：始终使用 Excel 公式而非硬编码计算值
2. **单元格索引**：openpyxl 使用 1 索引（row=1, column=1 是 A1）
3. **大文件处理**：使用 `read_only=True` 或 `write_only=True`
4. **数据类型**：指定数据类型避免推断问题
5. **保存前验证**：检查公式和数据完整性

## 完整示例：销售报表

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.chart import BarChart, Reference

def create_sales_report():
    wb = Workbook()
    sheet = wb.active
    sheet.title = "销售报表"

    # 表头
    headers = ['产品', 'Q1', 'Q2', 'Q3', 'Q4', '总计']
    sheet.append(headers)

    # 数据
    products = [
        ['产品A', 1000, 1200, 1400, 1600],
        ['产品B', 800, 900, 1100, 1300],
        ['产品C', 1500, 1600, 1800, 2000]
    ]

    for product in products:
        sheet.append(product)

    # 添加总计公式
    for row in range(2, 5):
        sheet[f'F{row}'] = f'=SUM(B{row}:E{row})'

    # 季度总计
    sheet['A5'] = '季度总计'
    for col in ['B', 'C', 'D', 'E', 'F']:
        sheet[f'{col}5'] = f'=SUM({col}2:{col}4)'

    # 格式化表头
    for cell in sheet[1]:
        cell.font = Font(bold=True, color='FFFFFF')
        cell.fill = PatternFill(start_color='4472C4', fill_type='solid')
        cell.alignment = Alignment(horizontal='center')

    # 格式化数字
    for row in range(2, 6):
        for col in ['B', 'C', 'D', 'E', 'F']:
            sheet[f'{col}{row}'].number_format = '#,##0'

    # 创建图表
    chart = BarChart()
    chart.title = "季度销售趋势"
    chart.x_axis.title = "产品"
    chart.y_axis.title = "销售额"

    data_ref = Reference(sheet, min_col=2, min_row=1, max_col=5, max_row=4)
    cats_ref = Reference(sheet, min_col=1, min_row=2, max_row=4)

    chart.add_data(data_ref, titles_from_data=True)
    chart.set_categories(cats_ref)

    sheet.add_chart(chart, "H2")

    # 保存
    wb.save('sales_report.xlsx')
    print("销售报表创建成功：sales_report.xlsx")

if __name__ == '__main__':
    create_sales_report()
```

## 更多资源

- [openpyxl 官方文档](https://openpyxl.readthedocs.io/)
- [pandas 官方文档](https://pandas.pydata.org/)
