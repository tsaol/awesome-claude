---
name: word
description: Word 文档创建、编辑和分析。支持跟踪修订、评论、格式保留和文本提取。当需要处理专业文档时使用：(1) 创建新文档，(2) 修改和编辑内容，(3) 处理跟踪修订，(4) 添加评论
---

# Word 文档处理技能

## 概述

本技能提供完整的 Word 文档处理能力，包括创建、编辑、格式化和跟踪修订功能。

## 功能特性

### 1. 读取文档内容

#### 使用 python-docx 读取

```python
from docx import Document

# 打开文档
doc = Document('document.docx')

# 读取所有段落
for paragraph in doc.paragraphs:
    print(paragraph.text)

# 读取表格
for table in doc.tables:
    for row in table.rows:
        for cell in row.cells:
            print(cell.text)

# 读取文档属性
print(f"段落数: {len(doc.paragraphs)}")
print(f"表格数: {len(doc.tables)}")
```

#### 提取纯文本

```python
from docx import Document

def extract_text(docx_path):
    doc = Document(docx_path)
    full_text = []

    for para in doc.paragraphs:
        full_text.append(para.text)

    return '\n'.join(full_text)

text = extract_text('document.docx')
print(text)
```

### 2. 创建新文档

```python
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

# 创建文档
doc = Document()

# 添加标题
doc.add_heading('文档标题', level=0)

# 添加段落
doc.add_paragraph('这是第一段文字。')

# 添加带格式的段落
p = doc.add_paragraph('这是')
p.add_run('粗体文字').bold = True
p.add_run('和')
p.add_run('斜体文字').italic = True

# 添加不同级别的标题
doc.add_heading('一级标题', level=1)
doc.add_paragraph('一级标题下的内容。')

doc.add_heading('二级标题', level=2)
doc.add_paragraph('二级标题下的内容。')

# 添加列表
doc.add_paragraph('第一项', style='List Bullet')
doc.add_paragraph('第二项', style='List Bullet')
doc.add_paragraph('第三项', style='List Bullet')

# 添加编号列表
doc.add_paragraph('第一步', style='List Number')
doc.add_paragraph('第二步', style='List Number')
doc.add_paragraph('第三步', style='List Number')

# 保存
doc.save('new_document.docx')
```

### 3. 文本格式化

```python
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = Document()

# 创建段落并设置格式
p = doc.add_paragraph()
run = p.add_run('格式化文本示例')

# 字体样式
run.font.name = 'Arial'
run.font.size = Pt(16)
run.font.bold = True
run.font.italic = False
run.font.underline = True
run.font.color.rgb = RGBColor(255, 0, 0)  # 红色

# 段落对齐
p.alignment = WD_ALIGN_PARAGRAPH.CENTER  # 居中
# 其他选项: LEFT, RIGHT, JUSTIFY

# 段落间距
from docx.shared import Inches
p.paragraph_format.space_before = Pt(12)
p.paragraph_format.space_after = Pt(12)
p.paragraph_format.line_spacing = 1.5

# 首行缩进
p.paragraph_format.first_line_indent = Inches(0.5)

doc.save('formatted_document.docx')
```

### 4. 添加表格

```python
from docx import Document
from docx.shared import Inches

doc = Document()

# 添加表格（3行4列）
table = doc.add_table(rows=3, cols=4)
table.style = 'Light Grid Accent 1'

# 填充表头
header_cells = table.rows[0].cells
header_cells[0].text = '产品'
header_cells[1].text = 'Q1'
header_cells[2].text = 'Q2'
header_cells[3].text = 'Q3'

# 填充数据
data = [
    ['产品A', '1000', '1200', '1400'],
    ['产品B', '800', '900', '1100']
]

for i, row_data in enumerate(data, start=1):
    cells = table.rows[i].cells
    for j, value in enumerate(row_data):
        cells[j].text = value

# 添加新行
row = table.add_row()
row.cells[0].text = '总计'

doc.save('table_document.docx')
```

### 5. 添加图片

```python
from docx import Document
from docx.shared import Inches

doc = Document()

# 添加图片
doc.add_heading('图片示例', level=1)
doc.add_picture('image.png', width=Inches(4))

# 添加带说明的图片
doc.add_paragraph('图片说明文字')

# 调整图片大小
picture = doc.add_picture('image.png')
picture.width = Inches(3)
picture.height = Inches(2)

doc.save('image_document.docx')
```

### 6. 添加页眉和页脚

```python
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = Document()

# 添加内容
doc.add_heading('文档内容', level=1)
doc.add_paragraph('这是文档的主要内容。')

# 获取页眉
section = doc.sections[0]
header = section.header
header_para = header.paragraphs[0]
header_para.text = "这是页眉"
header_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

# 获取页脚
footer = section.footer
footer_para = footer.paragraphs[0]
footer_para.text = "这是页脚 - 第 页"
footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

doc.save('header_footer_document.docx')
```

### 7. 编辑现有文档

```python
from docx import Document

# 打开现有文档
doc = Document('existing.docx')

# 修改段落文字
for paragraph in doc.paragraphs:
    if '旧文字' in paragraph.text:
        # 注意：直接替换会丢失格式
        paragraph.text = paragraph.text.replace('旧文字', '新文字')

# 在文档末尾添加内容
doc.add_page_break()
doc.add_heading('新增章节', level=1)
doc.add_paragraph('这是新添加的内容。')

# 修改表格
for table in doc.tables:
    # 修改第一个单元格
    table.rows[0].cells[0].text = '更新的内容'

# 保存（可以保存为新文件）
doc.save('modified_document.docx')
```

### 8. 添加超链接

```python
from docx import Document
from docx.oxml.shared import OxmlElement
from docx.oxml.ns import qn

def add_hyperlink(paragraph, text, url):
    """为段落添加超链接"""
    part = paragraph.part
    r_id = part.relate_to(url, 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink', is_external=True)

    hyperlink = OxmlElement('w:hyperlink')
    hyperlink.set(qn('r:id'), r_id)

    new_run = OxmlElement('w:r')
    rPr = OxmlElement('w:rPr')

    new_run.append(rPr)
    new_run.text = text
    hyperlink.append(new_run)

    paragraph._element.append(hyperlink)
    return hyperlink

doc = Document()
p = doc.add_paragraph('访问 ')
add_hyperlink(p, 'Google', 'https://www.google.com')

doc.save('hyperlink_document.docx')
```

### 9. 文档样式

```python
from docx import Document
from docx.shared import Pt

doc = Document()

# 使用内置样式
doc.add_paragraph('正常文本', style='Normal')
doc.add_paragraph('标题1', style='Heading 1')
doc.add_paragraph('标题2', style='Heading 2')
doc.add_paragraph('引用文字', style='Quote')
doc.add_paragraph('强调文字', style='Intense Quote')

# 列表样式
doc.add_paragraph('项目1', style='List Bullet')
doc.add_paragraph('项目2', style='List Bullet')
doc.add_paragraph('编号1', style='List Number')
doc.add_paragraph('编号2', style='List Number')

doc.save('styled_document.docx')
```

### 10. 分节和分页

```python
from docx import Document
from docx.enum.section import WD_SECTION, WD_ORIENT
from docx.shared import Inches

doc = Document()

# 第一节
doc.add_heading('第一章', level=1)
doc.add_paragraph('第一章的内容。')

# 添加分页符
doc.add_page_break()

# 第二节（横向）
doc.add_heading('第二章', level=1)
section = doc.sections[-1]
section.orientation = WD_ORIENT.LANDSCAPE
section.page_width = Inches(11)
section.page_height = Inches(8.5)

doc.add_paragraph('第二章的内容（横向页面）。')

# 添加连续分节符（不分页）
section = doc.add_section(WD_SECTION.CONTINUOUS)

doc.save('sections_document.docx')
```

## 处理跟踪修订

### 使用 pandoc 查看修订

```bash
# 显示所有跟踪修订
pandoc --track-changes=all document.docx -o output.md

# 接受所有修订
pandoc --track-changes=accept document.docx -o output.md

# 拒绝所有修订
pandoc --track-changes=reject document.docx -o output.md
```

## 文档转换

### DOCX 转 PDF

```bash
# 使用 LibreOffice 转换
soffice --headless --convert-to pdf document.docx
```

### DOCX 转 HTML

```bash
# 使用 pandoc
pandoc document.docx -o output.html
```

### DOCX 转 Markdown

```bash
pandoc document.docx -o output.md
```

## 实用函数

### 查找和替换

```python
from docx import Document

def find_replace(doc_path, find_text, replace_text, output_path):
    """查找并替换文档中的文字"""
    doc = Document(doc_path)

    # 替换段落中的文字
    for paragraph in doc.paragraphs:
        if find_text in paragraph.text:
            paragraph.text = paragraph.text.replace(find_text, replace_text)

    # 替换表格中的文字
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                if find_text in cell.text:
                    cell.text = cell.text.replace(find_text, replace_text)

    doc.save(output_path)

# 使用
find_replace('input.docx', '旧公司名', '新公司名', 'output.docx')
```

### 提取表格数据

```python
from docx import Document
import pandas as pd

def table_to_dataframe(table):
    """将 Word 表格转换为 pandas DataFrame"""
    data = []
    for row in table.rows:
        row_data = [cell.text for cell in row.cells]
        data.append(row_data)

    # 假设第一行是表头
    df = pd.DataFrame(data[1:], columns=data[0])
    return df

doc = Document('document.docx')
if doc.tables:
    df = table_to_dataframe(doc.tables[0])
    print(df)
    df.to_excel('table_data.xlsx', index=False)
```

### 统计文档信息

```python
from docx import Document

def document_stats(doc_path):
    """统计文档信息"""
    doc = Document(doc_path)

    stats = {
        '段落数': len(doc.paragraphs),
        '表格数': len(doc.tables),
        '总字数': 0,
        '非空段落': 0
    }

    for para in doc.paragraphs:
        if para.text.strip():
            stats['非空段落'] += 1
            stats['总字数'] += len(para.text)

    return stats

stats = document_stats('document.docx')
for key, value in stats.items():
    print(f"{key}: {value}")
```

## 完整示例：生成报告

```python
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

def create_report():
    doc = Document()

    # 封面
    title = doc.add_heading('年度工作报告', level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph()
    subtitle = doc.add_paragraph('2024年度总结')
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_page_break()

    # 目录（手动）
    doc.add_heading('目录', level=1)
    doc.add_paragraph('1. 工作概述')
    doc.add_paragraph('2. 主要成就')
    doc.add_paragraph('3. 数据分析')
    doc.add_paragraph('4. 未来规划')

    doc.add_page_break()

    # 第一章
    doc.add_heading('1. 工作概述', level=1)
    doc.add_paragraph(
        '本年度我们团队完成了多项重要任务，取得了显著成果。'
        '以下是详细的工作总结。'
    )

    # 第二章
    doc.add_heading('2. 主要成就', level=1)
    doc.add_paragraph('本年度主要成就包括：', style='List Bullet')
    achievements = [
        '完成项目A，提升效率30%',
        '开发新产品B，获得客户好评',
        '团队规模扩大到50人'
    ]
    for item in achievements:
        doc.add_paragraph(item, style='List Bullet')

    # 第三章 - 数据表格
    doc.add_heading('3. 数据分析', level=1)

    table = doc.add_table(rows=4, cols=4)
    table.style = 'Light Grid Accent 1'

    # 表头
    headers = ['季度', 'Q1', 'Q2', 'Q3']
    for i, header in enumerate(headers):
        table.rows[0].cells[i].text = header

    # 数据
    data = [
        ['销售额', '100万', '120万', '150万'],
        ['利润', '20万', '25万', '35万'],
        ['客户数', '500', '650', '800']
    ]

    for i, row_data in enumerate(data, start=1):
        for j, value in enumerate(row_data):
            table.rows[i].cells[j].text = value

    # 第四章
    doc.add_page_break()
    doc.add_heading('4. 未来规划', level=1)
    doc.add_paragraph('展望未来，我们将：')
    plans = [
        '继续深化产品创新',
        '拓展国际市场',
        '加强团队建设'
    ]
    for plan in plans:
        doc.add_paragraph(plan, style='List Number')

    # 保存
    doc.save('annual_report.docx')
    print('报告创建成功：annual_report.docx')

if __name__ == '__main__':
    create_report()
```

## 常用样式

```python
# 内置段落样式
'Normal'           # 正常文本
'Heading 1'        # 一级标题
'Heading 2'        # 二级标题
'Heading 3'        # 三级标题
'Title'            # 标题
'Subtitle'         # 副标题
'Quote'            # 引用
'Intense Quote'    # 强调引用
'List Bullet'      # 项目符号列表
'List Number'      # 编号列表
'List Continue'    # 列表延续
'Caption'          # 图片说明
```

## 依赖安装

```bash
# 安装 python-docx
pip install python-docx

# 安装 pandoc（用于格式转换）
sudo apt-get install pandoc

# 安装 LibreOffice（用于转 PDF）
sudo apt-get install libreoffice
```

## 快速参考

| 任务 | 代码示例 |
|------|----------|
| 创建文档 | `doc = Document()` |
| 添加标题 | `doc.add_heading('标题', level=1)` |
| 添加段落 | `doc.add_paragraph('文本')` |
| 添加表格 | `doc.add_table(rows=3, cols=4)` |
| 添加图片 | `doc.add_picture('image.png')` |
| 添加分页符 | `doc.add_page_break()` |
| 保存文档 | `doc.save('output.docx')` |
| 打开文档 | `doc = Document('file.docx')` |

## 最佳实践

1. **使用样式**：优先使用内置样式而非手动格式化
2. **结构化**：使用标题级别构建文档结构
3. **格式一致**：保持字体、间距的一致性
4. **测试保存**：修改后立即测试保存和打开
5. **备份原文件**：编辑现有文档前先备份

## 更多资源

- [python-docx 官方文档](https://python-docx.readthedocs.io/)
- [pandoc 官方文档](https://pandoc.org/)
