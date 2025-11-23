---
name: pdf
description: PDF 文档处理工具包，用于提取文本和表格、创建新 PDF、合并/分割文档、处理表单。当需要程序化处理、生成或分析 PDF 文档时使用
---

# PDF 文档处理技能

## 概述

本技能提供完整的 PDF 处理能力，包括文本提取、表格提取、PDF 创建、合并分割、表单填写等功能。

## 功能特性

### 1. 读取 PDF 基本信息

```python
from pypdf import PdfReader

# 读取 PDF
reader = PdfReader("document.pdf")

# 基本信息
print(f"页数: {len(reader.pages)}")

# 获取元数据
meta = reader.metadata
print(f"标题: {meta.title}")
print(f"作者: {meta.author}")
print(f"创建者: {meta.creator}")
```

### 2. 提取文本

```python
from pypdf import PdfReader

# 提取所有文本
reader = PdfReader("document.pdf")
text = ""
for page in reader.pages:
    text += page.extract_text()

print(text)
```

#### 使用 pdfplumber 提取文本（保留布局）

```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        print(text)
```

### 3. 提取表格

```python
import pdfplumber
import pandas as pd

with pdfplumber.open("document.pdf") as pdf:
    all_tables = []

    for i, page in enumerate(pdf.pages):
        tables = page.extract_tables()

        for j, table in enumerate(tables):
            print(f"第 {i+1} 页，表格 {j+1}:")

            # 转换为 DataFrame
            if table:
                df = pd.DataFrame(table[1:], columns=table[0])
                all_tables.append(df)
                print(df)
                print()

    # 合并所有表格并保存
    if all_tables:
        combined_df = pd.concat(all_tables, ignore_index=True)
        combined_df.to_excel("extracted_tables.xlsx", index=False)
```

### 4. 合并 PDF

```python
from pypdf import PdfWriter, PdfReader

# 创建写入器
writer = PdfWriter()

# 添加多个 PDF
pdf_files = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
for pdf_file in pdf_files:
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        writer.add_page(page)

# 保存合并后的 PDF
with open("merged.pdf", "wb") as output:
    writer.write(output)
```

### 5. 分割 PDF

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("input.pdf")

# 将每一页保存为单独的文件
for i, page in enumerate(reader.pages):
    writer = PdfWriter()
    writer.add_page(page)

    with open(f"page_{i+1}.pdf", "wb") as output:
        writer.write(output)

print(f"已分割为 {len(reader.pages)} 个文件")
```

#### 提取特定页面范围

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("input.pdf")
writer = PdfWriter()

# 提取第 2-5 页
for i in range(1, 5):  # 索引从 0 开始
    writer.add_page(reader.pages[i])

with open("pages_2_to_5.pdf", "wb") as output:
    writer.write(output)
```

### 6. 旋转页面

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("input.pdf")
writer = PdfWriter()

# 旋转第一页 90 度
page = reader.pages[0]
page.rotate(90)  # 顺时针旋转 90 度
writer.add_page(page)

# 其他页面保持不变
for i in range(1, len(reader.pages)):
    writer.add_page(reader.pages[i])

with open("rotated.pdf", "wb") as output:
    writer.write(output)
```

### 7. 创建 PDF

```python
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

# 创建 PDF
c = canvas.Canvas("hello.pdf", pagesize=letter)
width, height = letter

# 添加文本
c.setFont("Helvetica", 20)
c.drawString(100, height - 100, "Hello World!")

c.setFont("Helvetica", 12)
c.drawString(100, height - 130, "这是使用 reportlab 创建的 PDF")

# 添加线条
c.line(100, height - 150, 400, height - 150)

# 添加矩形
c.rect(100, height - 200, 200, 50)

# 保存
c.save()
```

### 8. 创建多页 PDF

```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

# 创建文档
doc = SimpleDocTemplate("report.pdf", pagesize=letter)
styles = getSampleStyleSheet()
story = []

# 第一页
title = Paragraph("报告标题", styles['Title'])
story.append(title)
story.append(Spacer(1, 0.5*inch))

content = Paragraph("这是报告的主要内容。" * 50, styles['Normal'])
story.append(content)
story.append(PageBreak())

# 第二页
story.append(Paragraph("第二页", styles['Heading1']))
story.append(Paragraph("第二页的内容", styles['Normal']))

# 生成 PDF
doc.build(story)
```

### 9. 添加水印

```python
from pypdf import PdfReader, PdfWriter

# 创建或加载水印 PDF
watermark = PdfReader("watermark.pdf").pages[0]

# 读取原文档
reader = PdfReader("document.pdf")
writer = PdfWriter()

# 为每一页添加水印
for page in reader.pages:
    page.merge_page(watermark)
    writer.add_page(page)

# 保存
with open("watermarked.pdf", "wb") as output:
    writer.write(output)
```

### 10. 密码保护

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("input.pdf")
writer = PdfWriter()

# 添加所有页面
for page in reader.pages:
    writer.add_page(page)

# 设置密码
writer.encrypt("userpassword", "ownerpassword")

# 保存加密的 PDF
with open("encrypted.pdf", "wb") as output:
    writer.write(output)
```

#### 解密 PDF

```python
from pypdf import PdfReader, PdfWriter

# 打开加密的 PDF
reader = PdfReader("encrypted.pdf")

# 如果需要密码
if reader.is_encrypted:
    reader.decrypt("userpassword")

# 创建无密码版本
writer = PdfWriter()
for page in reader.pages:
    writer.add_page(page)

with open("decrypted.pdf", "wb") as output:
    writer.write(output)
```

### 11. OCR 扫描件

```python
import pytesseract
from pdf2image import convert_from_path

# 将 PDF 转换为图片
images = convert_from_path('scanned.pdf')

# 对每一页进行 OCR
text = ""
for i, image in enumerate(images):
    text += f"第 {i+1} 页:\n"
    text += pytesseract.image_to_string(image, lang='chi_sim+eng')
    text += "\n\n"

# 保存提取的文本
with open('extracted_text.txt', 'w', encoding='utf-8') as f:
    f.write(text)

print("OCR 完成")
```

### 12. 提取图片

```bash
# 使用 pdfimages 命令行工具（需要 poppler-utils）
pdfimages -j input.pdf output_prefix

# 这会提取所有图片为 output_prefix-000.jpg, output_prefix-001.jpg 等
```

#### 使用 Python 提取图片

```python
from pypdf import PdfReader
import io
from PIL import Image

reader = PdfReader("document.pdf")

for page_num, page in enumerate(reader.pages):
    if '/XObject' in page['/Resources']:
        xObject = page['/Resources']['/XObject'].get_object()

        for obj in xObject:
            if xObject[obj]['/Subtype'] == '/Image':
                size = (xObject[obj]['/Width'], xObject[obj]['/Height'])
                data = xObject[obj].get_data()

                # 保存图片
                image = Image.open(io.BytesIO(data))
                image.save(f"page_{page_num}_image_{obj[1:]}.png")

print("图片提取完成")
```

## 命令行工具

### pdftotext（提取文本）

```bash
# 提取文本
pdftotext input.pdf output.txt

# 保留布局
pdftotext -layout input.pdf output.txt

# 提取特定页面
pdftotext -f 1 -l 5 input.pdf output.txt  # 第 1-5 页
```

### qpdf（合并和操作）

```bash
# 合并 PDF
qpdf --empty --pages file1.pdf file2.pdf -- merged.pdf

# 提取页面
qpdf input.pdf --pages . 1-5 -- pages1-5.pdf

# 旋转页面
qpdf input.pdf output.pdf --rotate=+90:1  # 旋转第 1 页 90 度

# 解密
qpdf --password=mypassword --decrypt encrypted.pdf decrypted.pdf
```

## 实用函数

### PDF 信息统计

```python
from pypdf import PdfReader

def pdf_stats(pdf_path):
    """获取 PDF 统计信息"""
    reader = PdfReader(pdf_path)

    stats = {
        '页数': len(reader.pages),
        '是否加密': reader.is_encrypted,
        '标题': reader.metadata.title if reader.metadata else None,
        '作者': reader.metadata.author if reader.metadata else None,
    }

    # 计算总字数
    total_words = 0
    for page in reader.pages:
        text = page.extract_text()
        total_words += len(text.split())

    stats['估计字数'] = total_words

    return stats

# 使用
info = pdf_stats('document.pdf')
for key, value in info.items():
    print(f"{key}: {value}")
```

### 批量处理 PDF

```python
from pypdf import PdfReader, PdfWriter
import os

def merge_pdfs_in_folder(folder_path, output_path):
    """合并文件夹中所有 PDF"""
    writer = PdfWriter()

    # 获取所有 PDF 文件并排序
    pdf_files = sorted([f for f in os.listdir(folder_path) if f.endswith('.pdf')])

    for pdf_file in pdf_files:
        file_path = os.path.join(folder_path, pdf_file)
        reader = PdfReader(file_path)

        for page in reader.pages:
            writer.add_page(page)

    with open(output_path, 'wb') as output:
        writer.write(output)

    print(f"已合并 {len(pdf_files)} 个文件")

# 使用
merge_pdfs_in_folder('pdf_folder', 'combined.pdf')
```

### 压缩 PDF

```bash
# 使用 Ghostscript 压缩 PDF
gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/ebook \
   -dNOPAUSE -dQUIET -dBATCH -sOutputFile=compressed.pdf input.pdf

# 压缩级别选项:
# /screen   - 最低质量，最小文件
# /ebook    - 中等质量（推荐）
# /printer  - 高质量
# /prepress - 最高质量
```

## 完整示例：PDF 报告生成器

```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

def create_sales_report():
    """创建销售报告 PDF"""
    doc = SimpleDocTemplate("sales_report.pdf", pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # 标题
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=30,
        alignment=1  # 居中
    )

    title = Paragraph("2024年度销售报告", title_style)
    story.append(title)
    story.append(Spacer(1, 0.5*inch))

    # 概述
    story.append(Paragraph("报告概述", styles['Heading2']))
    story.append(Paragraph(
        "本报告总结了2024年度的销售业绩，包括季度数据分析和增长趋势。",
        styles['Normal']
    ))
    story.append(Spacer(1, 0.3*inch))

    # 数据表格
    story.append(Paragraph("季度销售数据", styles['Heading2']))

    data = [
        ['产品', 'Q1', 'Q2', 'Q3', 'Q4', '总计'],
        ['产品A', '100万', '120万', '150万', '180万', '550万'],
        ['产品B', '80万', '90万', '110万', '130万', '410万'],
        ['产品C', '150万', '160万', '180万', '200万', '690万'],
        ['总计', '330万', '370万', '440万', '510万', '1650万']
    ]

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    story.append(table)
    story.append(Spacer(1, 0.5*inch))

    # 分页
    story.append(PageBreak())

    # 第二页：分析
    story.append(Paragraph("数据分析", styles['Heading2']))

    analysis_points = [
        "全年销售额稳步增长，同比增长25%",
        "产品C表现最佳，占总销售额的42%",
        "Q4销售创新高，达到510万元",
        "客户满意度提升至95%"
    ]

    for point in analysis_points:
        story.append(Paragraph(f"• {point}", styles['Normal']))
        story.append(Spacer(1, 0.1*inch))

    # 生成 PDF
    doc.build(story)
    print("销售报告生成成功：sales_report.pdf")

if __name__ == '__main__':
    create_sales_report()
```

## 快速参考

| 任务 | 最佳工具 | 代码示例 |
|------|----------|----------|
| 合并 PDF | pypdf | `writer.add_page(page)` |
| 分割 PDF | pypdf | 每页单独保存 |
| 提取文本 | pdfplumber | `page.extract_text()` |
| 提取表格 | pdfplumber | `page.extract_tables()` |
| 创建 PDF | reportlab | Canvas 或 Platypus |
| 命令行合并 | qpdf | `qpdf --empty --pages ...` |
| OCR 扫描件 | pytesseract | 先转图片再 OCR |
| 填写表单 | pypdf | 见官方文档 |

## 依赖安装

```bash
# 基础 PDF 操作
pip install pypdf

# 文本和表格提取
pip install pdfplumber

# 创建 PDF
pip install reportlab

# OCR 功能
pip install pytesseract pdf2image
sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim

# 命令行工具
sudo apt-get install poppler-utils  # pdftotext, pdfimages
sudo apt-get install qpdf            # qpdf
sudo apt-get install ghostscript     # PDF 压缩
```

## 注意事项

1. **索引从 0 开始**：页面索引从 0 开始，第一页是 `pages[0]`
2. **编码问题**：处理中文时注意编码设置
3. **内存占用**：处理大文件时注意内存使用
4. **字体支持**：创建 PDF 时确保字体可用
5. **加密文件**：需要先解密才能操作

## 更多资源

- [pypdf 官方文档](https://pypdf.readthedocs.io/)
- [pdfplumber 官方文档](https://github.com/jsvine/pdfplumber)
- [reportlab 官方文档](https://www.reportlab.com/docs/reportlab-userguide.pdf)
