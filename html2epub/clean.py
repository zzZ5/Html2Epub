#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Included modules / 内置模块
import re

# Third party modules / 第三方模块
import bs4
from bs4 import BeautifulSoup


# Local modules / 本地模块
from . import constants


def create_html_from_fragment(tag):
    """
    Creates full html tree from a fragment. Assumes that tag should be wrapped in a body and is currently not
    从片段创建完整的html树. 假设标签应该包装在body中，并且当前没有

    Parameters:
        tag: a bs4.element.Tag / bs4.element.Tag对象

    Returns:"
        bs4.element.Tag: A bs4 tag representing a full html document / 表示完整html文档的bs4标签
    """

    try:
        assert isinstance(tag, bs4.element.Tag)
    except AssertionError:
        raise TypeError
    try:
        assert tag.find_all('body') == []
    except AssertionError:
        raise ValueError

    soup = BeautifulSoup(
        '<html><head></head><body></body></html>', 'html.parser')
    soup.body.append(tag)
    return soup


def clean(input_string,
          tag_dictionary=constants.SUPPORTED_TAGS):
    """
    Sanitizes HTML. Tags not contained as keys in the tag_dictionary input are
    removed, and child nodes are recursively moved to parent of removed node.
    Attributes not contained as arguments in tag_dictionary are removed.
    Doctype is set to <!DOCTYPE html>.
    清理HTML. 不在tag_dictionary输入中的键中的标签将被删除，子节点递归移动到已删除节点的父节点。
    不在tag_dictionary参数中的属性将被删除。Doctype设置为<!DOCTYPE html>。

    Parameters:
        input_string (basestring): A (possibly unicode) string representing HTML.
            (可能是unicode)表示HTML的字符串。
        tag_dictionary (Option[dict]): A dictionary with tags as keys and
            attributes as values. This operates as a whitelist--i.e. if a tag
            isn't contained, it will be removed. By default, this is set to
            use the supported tags and attributes for the Amazon Kindle,
            as found at https://kdp.amazon.com/help?topicId=A1JPUWCSD6F59O
            以标签为键、属性为值的字典。这作为白名单操作——即如果标签
            不包含在其中，它将被删除。默认情况下，这设置为使用Amazon Kindle
            支持的标签和属性，如https://kdp.amazon.com/help?topicId=A1JPUWCSD6F59O所示

    Returns:
        str: A (possibly unicode) string representing HTML.
            (可能是unicode)表示HTML的字符串。

    Raises:
        TypeError: Raised if input_string isn't a unicode string or string.
            如果input_string不是unicode字符串或string则抛出。
    """
    try:
        assert isinstance(input_string, str)
    except AssertionError:
        raise TypeError
    root = BeautifulSoup(input_string, 'html.parser')
    article_tag = root.find_all('article')
    if article_tag:
        root = article_tag[0]
    stack = root.findAll(True, recursive=False)
    while stack:
        current_node = stack.pop()
        child_node_list = current_node.findAll(True, recursive=False)
        if current_node.name not in tag_dictionary.keys():
            parent_node = current_node.parent
            current_node.extract()
            for n in child_node_list:
                parent_node.append(n)
        else:
            attribute_dict = current_node.attrs
            for attribute in list(attribute_dict.keys()):
                if attribute not in tag_dictionary[current_node.name]:
                    attribute_dict.pop(attribute)
        stack.extend(child_node_list)
    # wrap partial tree if necessary / 必要时包装部分树
    if root.find_all('html') == []:
        root = create_html_from_fragment(root)
    # Remove img tags without src attribute / 删除没有src属性的img标签
    image_node_list = root.find_all('img')
    for node in image_node_list:
        if not node.has_attr('src'):
            node.extract()
    unformatted_html_unicode_string = root.prettify()
    # fix <br> tags since not handled well by default by bs4 / 修复<br>标签，因为bs4默认处理不好
    unformatted_html_unicode_string = unformatted_html_unicode_string.replace(
        '<br>', '<br/>')
    # remove &nbsp; and replace with space since not handled well by certain e-readers / 删除&nbsp;并用空格替换，因为某些电子阅读器处理不好
    unformatted_html_unicode_string = unformatted_html_unicode_string.replace(
        '&nbsp;', ' ')
    return unformatted_html_unicode_string


def condense(input_string):
    """
    Trims leadings and trailing whitespace between tags in an html document
    修剪html文档中标签之间前导和尾随空格

    Parameters:
        input_string: A (possible unicode) string representing HTML.
            (可能是unicode)表示HTML的字符串。

    Returns:
        A (possibly unicode) string representing HTML.
            (可能是unicode)表示HTML的字符串。

    Raises:
        TypeError: Raised if input_string isn't a unicode string or string.
            如果input_string不是unicode字符串或string则抛出。
    """
    try:
        assert isinstance(input_string, str)
    except AssertionError:
        raise TypeError
    removed_leading_whitespace = re.sub(r'>\s+', '>', input_string).strip()
    removed_trailing_whitespace = re.sub(
        r'\s+<', '<', removed_leading_whitespace).strip()
    return removed_trailing_whitespace


def html_to_xhtml(html_unicode_string):
    """
    Converts html to xhtml
    将html转换为xhtml

    Parameters:
        html_unicode_string: A (possible unicode) string representing HTML.
            (可能是unicode)表示HTML的字符串。

    Returns:
        A (possibly unicode) string representing XHTML.
            (可能是unicode)表示XHTML的字符串。

    Raises:
        TypeError: Raised if input_string isn't a unicode string or string.
            如果input_string不是unicode字符串或string则抛出。
    """
    try:
        assert isinstance(html_unicode_string, str)
    except AssertionError:
        raise TypeError
    root = BeautifulSoup(html_unicode_string, 'html.parser')
    # Confirm root node is html / 确认根节点是html
    try:
        assert root.html is not None
    except AssertionError:
        raise ValueError(''.join(['html_unicode_string cannot be a fragment.',
                                  'string is the following: %s', root]))
    # Add xmlns attribute to html node / 将xmlns属性添加到html节点
    root.html['xmlns'] = 'http://www.w3.org/1999/xhtml'
    unicode_string = root.prettify()
    # Close singleton tag_dictionary / 关闭单例标签
    for tag in constants.SINGLETON_TAG_LIST:
        unicode_string = unicode_string.replace(
            '<' + tag + '/>',
            '<' + tag + ' />')
    return unicode_string
