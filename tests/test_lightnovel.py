#!/usr/bin/python37
# -*- coding : utf-8 -*-
import os
import sys
from urllib.parse import urlparse
import re


from bs4 import BeautifulSoup
import requests


import html2epub

DIR = "d:\\Users\\baoju\\Desktop\\books\\"  # 输出epub文件的路径


html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
</head>
<body>
{content}
</body>
</html>

"""


def getbook(url):    # 获取整本书并写入文本
    try:
        r = requests.request('GET', url)
    except:
        print("分析失败了, 稍后再试吧")
        sys.exit()

    domain = '{uri.scheme}://{uri.netloc}'.format(
        uri=urlparse(url))
    soup = BeautifulSoup(r.text, 'html.parser')
    name = soup.title.string
    bookName = re.sub(r'[\/:*?"<>|]', '-', name)
    tags = soup.find_all('td', class_='t_f')
    htmls = []
    for eachTag in tags:
        html = str(eachTag)
        html = html.replace("file", "src")
        html = html.replace("td", "div")
        # html中的img标签的src相对路径的改成绝对路径
        pattern = "(<img .*?src=\")(.*?)(\")"

        def func(m):
            if not m.group(2).startswith("http"):
                rtn = "".join(
                    [m.group(1), domain, m.group(2), m.group(3)])
                return rtn
            else:
                return "".join([m.group(1), m.group(2), m.group(3)])

        html = re.compile(pattern).sub(func, html)
        html = html_template.format(content=html)
        htmls.append(html)
    print("下载完毕, 准备整合epub")
    return bookName, htmls


def saveEpub(url):

    bookName, htmls = getbook(url)
    epub = html2epub.Epub(bookName)
    i = 0
    print("开始整合epub...")
    for eachHtml in htmls:
        i += 1
        chapter = html2epub.create_chapter_from_string(
            eachHtml, title="章节" + str(i))
        epub.add_chapter(chapter)
        print("已整合{:.2f}%".format(
            (htmls.index(eachHtml) + 1) / len(htmls) * 100))
    epub.create_epub(DIR)
    print("整合完毕.")


if __name__ == "__main__":    # 主函数
    # URL = input("请输入要下载的网址: ")    # 获取地址
    # print("url为: " + URL + "\n开始下载...")
    URL = "https://www.lightnovel.cn/forum.php?mod=viewthread&tid=989498&page=1&authorid=1078151"

    saveEpub(URL)
