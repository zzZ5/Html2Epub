# html2epub

## 简介 / Introduction

原项目为 python2 项目 [pypub](https://github.com/wcember/pypub)，此为 python3 项目，并进行了些许修改与优化。

This project is a Python 3 fork of the original [pypub](https://github.com/wcember/pypub) (Python 2), with various improvements and optimizations.

将 HTML 链接、HTML 文件或 HTML 文本转换成 EPUB 文件。

Converts HTML links, HTML files, or HTML text into EPUB files.

> **tips / 提示**
>
> 关于 EPUB 文件的格式可以参考 [EPUB - Wikipedia](https://en.wikipedia.org/wiki/EPUB)。
>
> For EPUB format details, refer to [EPUB - Wikipedia](https://en.wikipedia.org/wiki/EPUB).

## 快速使用 / Quick Start

```python
>>> import html2epub
>>> epub = html2epub.Epub('My First Epub')
>>> chapter = html2epub.create_chapter_from_url('https://en.wikipedia.org/wiki/EPUB')
>>> epub.add_chapter(chapter)
>>> epub.create_epub('OUTPUT_DIRECTORY')
```

## 安装 / Installation

```bash
pip install beautifulsoup4 jinja2 lxml requests
# 或使用 requirements.txt
# or install from requirements.txt
pip install -r requirements.txt
```

## 功能特性 / Features

- 从 URL 创建章节 / Create chapters from URLs
- 从 HTML 文件创建章节 / Create chapters from HTML files
- 从 HTML 字符串创建章节 / Create chapters from HTML strings
- 自动清理 HTML 内容 / Automatically clean HTML content
- 支持 CSS 样式 / Support CSS styles
- 支持图片嵌入 / Support image embedding
- 完整的元数据支持 / Full metadata support

## API 参考 / API Reference

### Epub 类 / Epub Class

```python
epub = html2epub.Epub('Book Title', author='Author Name')
epub.add_chapter(chapter)
epub.set_cover('cover.jpg')
epub.create_epub('output_directory')
```

### 创建章节 / Creating Chapters

```python
# 从 URL 创建 / Create from URL
chapter = html2epub.create_chapter_from_url('https://example.com')

# 从文件创建 / Create from file
chapter = html2epub.create_chapter_from_file('path/to/file.html')

# 从字符串创建 / Create from string
chapter = html2epub.create_chapter_from_string('<h1>Hello</h1><p>World</p>')
```

## 测试 / Testing

```bash
python run_tests.py
```

## Python 版本支持 / Python Version Support

- Python 3.8+
- 已测试并兼容 Python 3.12 和 3.13 / Tested and compatible with Python 3.12 and 3.13

## 参考文献 / References

1. *[wcember/pypub: Python library to programatically create epub files](https://github.com/wcember/pypub).*
2. *[EPUB - Wikipedia](https://en.wikipedia.org/wiki/EPUB).*

## 许可证 / License

MIT License
