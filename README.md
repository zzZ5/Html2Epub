# html2epub

## 简介

原项目为python2项目 [pypub](https://github.com/wcember/pypub) , 此为python3项目, 并进行了些许修改

将 html链接, html文件 或 html文本 转换成 epub文件.

## 快速使用

```python
>>> import html2epub
>>> epub = pypub.Epub('My First Epub')
>>> chapter = pypub.create_chapter_from_url('https://en.wikipedia.org/wiki/EPUB')
>>> epub.add_chapter(my_first_chapter)
>>> epub.create_epub('OUTPUT_DIRECTORY')
```

## 参考文献

1. *[wcember/pypub: Python library to programatically create epub files](https://github.com/wcember/pypub)*
