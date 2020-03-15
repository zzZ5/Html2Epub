#!/usr/bin/python37
# -*- coding : utf-8 -*-
import os
import sys
from urllib.parse import urlparse
import re


import requests
from bs4 import BeautifulSoup


import html2epub

DIR = "c:\\Users\\baoju\\Desktop\\"  # 输出epub文件的路径

headers = {
    "cookie": "__cfduid=de9a30d2f3eb64f5a497759abab0a2ec91563444452; xxzo_2132_saltkey=mC8BccM9; xxzo_2132_lastvisit=1563440852; xxzo_2132_nofavfid=1; xxzo_2132_smile=1D1; xxzo_2132_auth=e72cRlanMgm5gv6bx13w6LSud1ubrWx6G%2BxKvJp1ZfIedrn9iFzLn7hMZ5LSCeSx7DgsyNhlmuCh5ujN8hyAUUxk; xxzo_2132_lastcheckfeed=9084%7C1565232143; xxzo_2132_sid=FmfHkM; xxzo_2132_lip=125.44.225.1%2C1565232676; xxzo_2132_onlineusernum=941; xxzo_2132_ulastactivity=d1d28Gd%2FJfBIoLE3E2WElQ6W7E75CaoRWHZ0%2FI9hG6MozwBraCZi; xxzo_2132_sendmail=1; xxzo_2132_checkpm=1; xxzo_2132_lastact=1565265308%09forum.php%09forumdisplay; xxzo_2132_st_t=9084%7C1565265308%7C097d78603fdb098dfd1144a026a61a76; xxzo_2132_forum_lastvisit=D_179_1565232434D_36_1565265292D_89_1565265308; xxzo_2132_visitedfid=89D36D179"
}

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


def getInfoList(URL):    # 获取所有章节网页地址和数名
    totalPage = 1    # 该书总页数, 默认为一

    r = requests.request('GET', URL)  # 获取主网页

    soup = BeautifulSoup(r.text, 'html.parser')
    infoList = []    # 储存所有章节地址
    pageTag = soup.find('span', title=re.compile(r"^共"))    # 获取总页数
    bookName = soup.title.string  # 获取书名
    bookName = re.sub(r'[\/:*?"<>|]', '-', bookName)
    if(pageTag):     # 如果只有一页的话是没有总页数的, 此时总页数为默认的1
        totalPage = int(pageTag['title'].split(' ')[1])
    for i in range(totalPage, 0, -1):     # 从所有网页获取全部章节, 由于章节排序反向, 所以页面反序
        url = URL + "&page={}".format(i)    # 按页数获取页面网址
        r = requests.request('GET', url)
        soup = BeautifulSoup(r.text, 'html.parser')
        tag = soup.findAll('a', class_="s xst",
                           text=re.compile(r"^[\d]|第"))  # 匹配章节网址
        for j in range(len(tag) - 1, -1, -1):     # 反向存如章节网址
            infoList.append(tag[j]['href'])
    return infoList, bookName


def getbook(infoList):    # 获取整本书并写入文本

    for i in range(len(infoList)):  # 访问所有章节地址
        try:
            r = requests.request('GET', infoList[i], headers=headers)
        except:
            print("分析失败了, 稍后再试吧")
            sys.exit()
        domain = '{uri.scheme}://{uri.netloc}'.format(
            uri=urlparse(infoList[i]))
        soup = BeautifulSoup(r.text, 'html.parser')
        title = soup.title.string    # 获取文章标题
        title = re.sub(r'[\/:*?"<>|]', '-', title)
        tag = soup.find_all('td', class_='t_f')[0]    # 获取文章所在的table
        html = str(tag)
        html = html.replace("td", "div")
        html = html.replace("file", "src")
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

        print("已完成{:.2f}%".format((i + 1) / len(infoList) * 100))
        yield html, title


def saveEpub(infoList, bookName):

    epub = html2epub.Epub(bookName)
    for eachHtml, title in getbook(infoList):
        chapter = html2epub.create_chapter_from_string(eachHtml, title=title)
        epub.add_chapter(chapter)
    epub.create_epub(DIR)
    print("下载成功, 已保存在: ", DIR + bookName + ".epub")


if __name__ == "__main__":    # 主函数
    # URL = input("请输入要下载的网址: ")    # 获取地址
    # print("url为: " + URL + "\n开始下载...")
    URL = "https://masiro.moe/forum.php?mod=forumdisplay&fid=89"

    infoList, bookName = getInfoList(URL)
    saveEpub(infoList, bookName)
