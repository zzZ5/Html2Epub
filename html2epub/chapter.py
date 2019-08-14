#!usr/bin/python3
# -*- coding: utf-8 -*-

# Included modules
import cgi
import codecs
import imghdr
import os
import shutil
import tempfile
import urllib
from urllib.parse import urljoin
import uuid

# Third party modules
import requests
import bs4
from bs4 import BeautifulSoup

# Local modules
from . import clean


class NoUrlError(Exception):
    def __str__(self):
        return 'Chapter instance URL attribute is None'


class ImageErrorException(Exception):
    def __init__(self, image_url):
        self.image_url = image_url

    def __str__(self):
        return 'Error downloading image from ' + self.image_url


def get_image_type(url):
    """
    获取图片的类型.

    Parameters:
        url(str): 图片路径.

    returns:
        str: 图片的类型名{'jpg', 'jpge', 'gif', 'png', None}

    raises:
        IOError: 图片类型不在 {'jpg', 'jpge', 'gif', 'png'} 四个类型之中
    """

    for ending in ['jpg', 'jpeg', 'gif' 'png']:
        if url.endswith(ending):
            return ending
    else:
        try:
            _, temp_file_name = tempfile.mkstemp()
            urllib.request.urlretrieve(url, temp_file_name)
            image_type = imghdr.what(temp_file_name)
            return image_type
        except IOError:
            return None


def save_image(image_url, image_directory, image_name):
    """
    保存在线图片到指定的路径, 可自定义文件名.

    Parameters:
        image_url (str): image路径.
        image_directory (str): 保存image的路径.
        image_name (str): image的文件名(无后缀).

    Raises:
        ImageErrorException: 在无法保存该图片时触发该 Error.

    Returns:
        str: 图片的类型.
    """
    image_type = get_image_type(image_url)
    if image_type is None:
        raise ImageErrorException(image_url)
    full_image_file_name = os.path.join(
        image_directory, image_name + '.' + image_type)

    # If the image is present on the local filesystem just copy it
    if os.path.exists(image_url):
        shutil.copy(image_url, full_image_file_name)
        return image_type

    try:
        # urllib.urlretrieve(image_url, full_image_file_name)
        with open(full_image_file_name, 'wb') as f:
            user_agent = r'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
            request_headers = {'User-Agent': user_agent}
            requests_object = requests.get(image_url, headers=request_headers)
            try:
                content = requests_object.content
                # Check for empty response
                f.write(content)
            except AttributeError:
                raise ImageErrorException(image_url)
    except IOError:
        raise ImageErrorException(image_url)
    return image_type


def _replace_image(image_url, image_tag, ebook_folder,
                   image_name=None):
    """
    将 image_tag 中的image下载到本地, 并将 image_tag 中img的src修改为本地src.

    Parameters:
        image_url (str): image的url.
        image_tag (bs4.element.Tag): bs4中包含image的tag.
        ebook_folder (str): 将外部图片保存到本地的地址. 内部一定要包含一个名为 "images" 的文件夹.
        image_name (Option[str]): 保存到本地的imgae的文件名(不包含后缀).

    Returns:
        str: image本地链接地址
        str: image的文件名(不包含后缀)
        str: image的类型 {'jpg', 'jpge', 'gif', 'png'} .
    """
    try:
        assert isinstance(image_tag, bs4.element.Tag)
    except AssertionError:
        raise TypeError("image_tag cannot be of type " + str(type(image_tag)))
    if image_name is None:
        image_name = str(uuid.uuid4())
    try:
        image_full_path = os.path.join(ebook_folder, 'images')
        assert os.path.exists(image_full_path)
        image_extension = save_image(image_url, image_full_path,
                                     image_name)
        image_link = 'images' + '/' + image_name + '.' + image_extension
        image_tag['src'] = image_link
        return image_link, image_name, image_extension
    except ImageErrorException:
        image_tag.decompose()
    except AssertionError:
        raise ValueError(
            '%s doesn\'t exist or doesn\'t contain a subdirectory images' % ebook_folder)
    except TypeError:
        image_tag.decompose()


class Chapter():
    """
    chapter对象类. 不能直接调用, 应该用 ChapterFactor() 去实例化chapter.

    Parameters:
        content (str): 章节内容. 必须为xhtml格式.
        title (str): 章节标题.
        url (Option[str]): 章节所在网页的URL(如果适用), 默认情况下为None.

    Attributes:
        content (str): 章节内容.
        title (str): 章节标题.
        url (str): 章节所在网页的URL(如果适用).
        html_title (str): 将特殊字符替换为html安全序列的标题字符串.
    """

    def __init__(self, content, title, url=None):
        self._validate_input_types(content, title)
        self.title = title
        self.content = content
        self._content_tree = BeautifulSoup(self.content, 'html.parser')
        self.url = url
        self.html_title = cgi.escape(self.title, quote=True)
        self.imgs = []

    def write(self, file_name):
        """
        将chapter内容写入 xhtml文件.

        Parameters:
            file_name (str): 要写入xhtml文件的全名(包含后缀).
        """
        try:
            assert file_name[-6:] == '.xhtml'
        except (AssertionError, IndexError):
            raise ValueError('filename must end with .xhtml')
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(self.content)

    def _validate_input_types(self, content, title):
        try:
            assert isinstance(content, str)
        except AssertionError:
            raise TypeError('content must be a string')
        try:
            assert isinstance(title, str)
        except AssertionError:
            raise TypeError('title must be a string')
        try:
            assert title != ''
        except AssertionError:
            raise ValueError('title cannot be empty string')
        try:
            assert content != ''
        except AssertionError:
            raise ValueError('content cannot be empty string')

    def get_url(self):
        if self.url is not None:
            return self.url
        else:
            raise NoUrlError()

    def _get_image_urls(self):
        image_nodes = self._content_tree.find_all('img')
        raw_image_urls = [node['src']
                          for node in image_nodes if node.has_attr('src')]
        full_image_urls = [urljoin(
            self.url, image_url) for image_url in raw_image_urls]
        image_nodes_filtered = [
            node for node in image_nodes if node.has_attr('src')]
        return zip(image_nodes_filtered, full_image_urls)

    def _replace_images_in_chapter(self, ebook_folder):
        image_url_list = self._get_image_urls()
        for image_tag, image_url in image_url_list:
            imgInfo = _replace_image(
                image_url, image_tag, ebook_folder)
            if imgInfo != None:
                img_link, img_id, img_type = imgInfo
                img = {'link': img_link, 'id': img_id, 'type': img_type}
                self.imgs.append(img)
        unformatted_html_unicode_string = self._content_tree.prettify()
        unformatted_html_unicode_string = unformatted_html_unicode_string.replace(
            '<br>', '<br/>')
        self.content = unformatted_html_unicode_string


class ChapterFactory():
    """
    用来创建 chapter的类. 可以从 url, 文件 或 文本 三个方式创建 chapter.

    Parameters:
        clean_function (Option[function]): 用于清扫要在epub中使用的原始html 的函数. 默认情况下, 这是html2epub.clean函数.
    """

    def __init__(self, clean_function=clean.clean):
        self.clean_function = clean_function
        user_agent = r'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20100101 Firefox/31.0'
        self.request_headers = {'User-Agent': user_agent}

    def create_chapter_from_url(self, url, title=None):
        """
        从URL创建chapter对象. 
        从给定的url中提取网页, 使用clean_function方法对其进行清理, 并将其另存为创建的chpter的内容.
        在执行任何javascript之前加载的基本网页.

        Parameters:
            url (string): 获取chapter对象的网页地址.
            title (Option[string]): chapter的章节名, 如果为None, 则使用从网页中获取的 title标签 的内容作为章节名.

        Returns:
            Chapter: 一个Chapter对象, 其内容是给定url的网页. 

        Raises:
            ValueError: 如果无法连接该url则触发此 Error.
        """
        try:
            request_object = requests.get(
                url, headers=self.request_headers, allow_redirects=False)
        except requests.exceptions.SSLError:
            raise ValueError("Url %s doesn't have valid SSL certificate" % url)
        except (requests.exceptions.MissingSchema,
                requests.exceptions.ConnectionError):
            raise ValueError(
                "%s is an invalid url or no network connection" % url)
        unicode_string = request_object.text
        return self.create_chapter_from_string(unicode_string, url, title)

    def create_chapter_from_file(self, file_name, url=None, title=None):
        """
        从html或xhtml文件创建chapter对象.
        使用clean_function方法清理文件的内容, 并将其另存为创建的chapter的内容.

        Parameters:
            file_name (string): 包含所创建chapter的html或xhtml内容的file_name.
            url (Option[string]): A url to infer the title of the chapter from
            title (Option[string]): chapter的章节名, 如果为None, 则使用从网页文件中获取的 title标签 的内容作为章节名.

        Returns:
            Chapter: 一个Chapter对象, 其内容是给定html或xhtml文件的内容.
        """
        with codecs.open(file_name, 'r', encoding='utf-8') as f:
            content_string = f.read()
        return self.create_chapter_from_string(content_string, url, title)

    def create_chapter_from_string(self, html_string, url=None, title=None):
        """
        从字符串创建chapter对象.
        使用clean_function方法清理字符串, 并将其另存为创建的chapter的内容.

        Parameters:
            html_string (string): 创建的chapter的html或xhtml内容.
            url (Option[string]): 推断章节标题的url
            title (Option[string]): chapter的章节名, 如果为None, 则使用从文本中获取的 title标签 的内容作为章节名.

        Returns:
            Chapter: 一个Chapter对象, 其内容是给定文本的内容.
        """
        clean_html_string = self.clean_function(html_string)
        clean_xhtml_string = clean.html_to_xhtml(clean_html_string)

        if title:
            pass
        else:
            try:
                root = BeautifulSoup(html_string, 'html.parser')
                title_node = root.title
                if title_node is not None:
                    title = title_node.string
                else:
                    raise ValueError
            except (IndexError, ValueError):
                title = 'Ebook Chapter'
        return Chapter(clean_xhtml_string, title, url)


create_chapter_from_url = ChapterFactory().create_chapter_from_url
create_chapter_from_file = ChapterFactory().create_chapter_from_file
create_chapter_from_string = ChapterFactory().create_chapter_from_string
