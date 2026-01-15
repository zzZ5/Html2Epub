#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HTML cleaning functionality tests
HTML清理功能测试
"""

import sys
import os
import unittest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from html2epub import clean


class TestHTMLCleaning(unittest.TestCase):
    """Test HTML cleaning functionality / 测试HTML清理功能"""

    def test_basic_html_cleaning(self):
        """Test basic HTML cleaning / 测试基本HTML清理"""
        html = '''
        <html>
        <head><title>Test</title></head>
        <body>
            <p>Paragraph 1</p>
            <p>Paragraph 2</p>
        </body>
        </html>
        '''
        result = clean.clean(html)
        
        self.assertIsNotNone(result)
        self.assertIn('<html', result.lower())
        self.assertIn('<body>', result.lower())

    def test_remove_unsupported_tags(self):
        """Test removal of unsupported tags / 测试移除不支持的标签"""
        html = '<div><p>Keep this</p><script>alert("remove")</script></div>'
        result = clean.clean(html)
        
        self.assertNotIn('<script', result.lower())
        self.assertIn('Keep this', result)

    def test_remove_unsupported_attributes(self):
        """Test removal of unsupported attributes / 测试移除不支持的属性"""
        html = '<p onclick="alert()">Text</p>'
        result = clean.clean(html)
        
        self.assertNotIn('onclick', result)
        # Pretty format will add newlines and indentation / 美化格式会添加换行和缩进
        self.assertIn('Text', result)

    def test_keep_supported_tags(self):
        """Test keeping supported tags / 测试保留支持的标签"""
        html = '<h1>Title</h1><p>Paragraph</p><b>Bold</b>'
        result = clean.clean(html)
        
        self.assertIn('<h1', result)
        self.assertIn('<p', result)
        self.assertIn('<b>', result)

    def test_image_src_attribute_kept(self):
        """Test keeping img src attribute / 测试保留img src属性"""
        html = '<img src="image.jpg" alt="Test" />'
        result = clean.clean(html)
        
        self.assertIn('src=', result)
        self.assertIn('image.jpg', result)

    def test_remove_img_without_src(self):
        """Test removing img tags without src / 测试移除没有src的img标签"""
        html = '<img alt="No src" />'
        result = clean.clean(html)
        
        self.assertNotIn('<img', result.lower())

    def test_br_tag_fixing(self):
        """Test fixing <br> tags / 测试修复<br>标签"""
        html = '<p>Line 1<br>Line 2</p>'
        result = clean.clean(html)
        
        self.assertIn('<br/>', result)
        self.assertNotIn('<br>', result.replace('<br/>', ''))

    def test_nbsp_replacement(self):
        """Test &nbsp; replacement / 测试&nbsp;替换"""
        html = '<p>Text&nbsp;with&nbsp;spaces</p>'
        result = clean.clean(html)
        
        self.assertNotIn('&nbsp;', result)
        self.assertIn(' ', result)

    def test_html_to_xhtml_conversion(self):
        """Test HTML to XHTML conversion / 测试HTML到XHTML转换"""
        html = '<html><head><title>Test</title></head><body><p>Content</p></body></html>'
        result = clean.html_to_xhtml(html)
        
        self.assertIn('xmlns=', result)
        self.assertIn('http://www.w3.org/1999/xhtml', result)

    def test_singleton_tag_spacing(self):
        """Test singleton tag spacing / 测试单例标签间距"""
        html = '<html><br /><img src="test.jpg" /><hr /></html>'
        result = clean.html_to_xhtml(html)
        
        # Check proper spacing / 检查正确的间距
        self.assertIn('<br />', result)
        self.assertIn('<hr />', result)

    def test_condense_whitespace(self):
        """Test whitespace condensing / 测试空白压缩"""
        html = '<p>  Extra  spaces  </p>'
        result = clean.condense(html)
        
        # Should reduce whitespace between tags / 应该减少标签之间的空白
        self.assertNotIn('  ', result.replace(' ', ''))

    def test_article_tag_extraction(self):
        """Test extracting article tag / 测试提取article标签"""
        html = '''
        <html>
        <body>
            <div>Outer content</div>
            <article>
                <h1>Article Title</h1>
                <p>Article content</p>
            </article>
        </body>
        </html>
        '''
        result = clean.clean(html)
        
        # Should extract article content / 应该提取article内容
        self.assertIn('Article Title', result)
        self.assertIn('Article content', result)

    def test_empty_input_handling(self):
        """Test handling of empty input / 测试处理空输入"""
        with self.assertRaises(TypeError):
            clean.clean(None)

    def test_complex_html_structure(self):
        """Test complex HTML structure / 测试复杂HTML结构"""
        html = '''
        <html>
        <head>
            <title>Complex Test</title>
            <style>body {color: red;}</style>
        </head>
        <body>
            <div class="container">
                <h1>Main Heading</h1>
                <p>First paragraph</p>
                <blockquote>Quote</blockquote>
                <ul>
                    <li>Item 1</li>
                    <li>Item 2</li>
                </ul>
            </div>
        </body>
        </html>
        '''
        result = clean.clean(html)
        
        # Should keep supported structure / 应该保留支持的结构
        self.assertIn('<h1', result)
        self.assertIn('<p>', result)
        self.assertIn('<blockquote>', result)
        # Should remove unsupported elements / 应该移除不支持的元素
        self.assertNotIn('<style', result.lower())


class TestFragmentWrapping(unittest.TestCase):
    """Test HTML fragment wrapping / 测试HTML片段包装"""

    def test_wrap_body_fragment(self):
        """Test wrapping body fragment / 测试包装body片段"""
        from bs4 import BeautifulSoup
        tag = BeautifulSoup('<p>Fragment</p>', 'html.parser').find('p')
        soup = clean.create_html_from_fragment(tag)
        
        self.assertIn('<html>', str(soup))
        self.assertIn('<body>', str(soup))
        self.assertIn('<p>Fragment</p>', str(soup))


if __name__ == '__main__':
    unittest.main(verbosity=2)
