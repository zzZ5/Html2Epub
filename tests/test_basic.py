#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Basic functionality tests for html2epub
html2epub基本功能测试
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import html2epub


class TestEpubBasic(unittest.TestCase):
    """Test basic epub creation functionality / 测试基本epub创建功能"""

    def setUp(self):
        """Set up test environment / 设置测试环境"""
        self.test_output_dir = 'test_output'
        if not os.path.exists(self.test_output_dir):
            os.makedirs(self.test_output_dir)

    def tearDown(self):
        """Clean up test files / 清理测试文件"""
        # Keep test output for inspection / 保留测试输出以便检查
        pass

    def test_create_epub_from_string(self):
        """Test creating epub from HTML string / 测试从HTML字符串创建epub"""
        epub = html2epub.Epub('Test Book')
        chapter = html2epub.create_chapter_from_string(
            '<h1>Chapter 1</h1><p>Test content</p>',
            title='First Chapter'
        )
        epub.add_chapter(chapter)
        path = epub.create_epub(self.test_output_dir, 'test_from_string')
        
        self.assertTrue(os.path.exists(path), f"EPUB file not created: {path}")
        self.assertTrue(path.endswith('.epub'), f"File should end with .epub: {path}")

    def test_create_epub_from_file(self):
        """Test creating epub from HTML file / 测试从HTML文件创建epub"""
        # Create temporary HTML file / 创建临时HTML文件
        html_content = '''<!DOCTYPE html>
<html>
<head><title>File Chapter</title></head>
<body>
    <h1>File Test</h1>
    <p>This is content from a file.</p>
</body>
</html>'''
        
        temp_file = 'temp_test.html'
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            epub = html2epub.Epub('File Test Book')
            chapter = html2epub.create_chapter_from_file(temp_file)
            epub.add_chapter(chapter)
            path = epub.create_epub(self.test_output_dir, 'test_from_file')
            
            self.assertTrue(os.path.exists(path), f"EPUB file not created: {path}")
            self.assertEqual(chapter.title, 'File Chapter', "Chapter title mismatch")
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def test_multiple_chapters(self):
        """Test creating epub with multiple chapters / 测试创建包含多个章节的epub"""
        epub = html2epub.Epub('Multi Chapter Book', creator='Test Author')
        
        chapters_count = 5
        for i in range(chapters_count):
            chapter = html2epub.create_chapter_from_string(
                f'<h1>Chapter {i+1}</h1><p>Content for chapter {i+1}</p>',
                title=f'Chapter {i+1}'
            )
            epub.add_chapter(chapter)
        
        path = epub.create_epub(self.test_output_dir, 'multi_chapter')
        
        self.assertTrue(os.path.exists(path), f"EPUB file not created: {path}")
        self.assertEqual(len(epub.chapters), chapters_count, 
                        "Chapter count mismatch")

    def test_epub_metadata(self):
        """Test epub metadata / 测试epub元数据"""
        title = 'Metadata Test'
        creator = 'Test Author'
        language = 'en'
        
        epub = html2epub.Epub(
            title=title,
            creator=creator,
            language=language
        )
        
        self.assertEqual(epub.title, title, "Title mismatch")
        self.assertEqual(epub.creator, creator, "Creator mismatch")
        self.assertEqual(epub.language, language, "Language mismatch")

    def test_empty_title_raises_error(self):
        """Test that empty title raises ValueError / 测试空标题引发ValueError"""
        with self.assertRaises(ValueError):
            html2epub.Epub('')

    def test_chapter_validation(self):
        """Test chapter input validation / 测试章节输入验证"""
        # Valid chapter should work / 有效章节应该工作
        chapter = html2epub.create_chapter_from_string(
            '<h1>Title</h1><p>Content</p>',
            title='Valid'
        )
        self.assertIsNotNone(chapter.content)
        
        # Empty title uses default title / 空标题使用默认标题
        chapter_with_empty_title = html2epub.create_chapter_from_string(
            '<p>Content</p>',
            title=''
        )
        self.assertEqual(chapter_with_empty_title.title, 'Ebook Chapter')
        
        # Very short content should still work / 非常短的内容仍然应该工作
        chapter_with_minimal = html2epub.create_chapter_from_string(
            '<p>.</p>',
            title='Minimal'
        )
        self.assertIsNotNone(chapter_with_minimal.content)


class TestChapterFactory(unittest.TestCase):
    """Test ChapterFactory functionality / 测试ChapterFactory功能"""

    def test_create_chapter_from_url_mock(self):
        """Test creating chapter from URL with mock / 测试使用mock从URL创建章节"""
        mock_html = '''<!DOCTYPE html>
<html>
<head><title>URL Test</title></head>
<body>
    <h1>URL Chapter</h1>
    <p>Content from URL</p>
</body>
</html>'''
        
        mock_response = Mock()
        mock_response.text = mock_html
        
        with patch('requests.get', return_value=mock_response):
            chapter = html2epub.create_chapter_from_url(
                'https://example.com/test',
                title='Custom Title'
            )
            
            self.assertEqual(chapter.title, 'Custom Title', "Title mismatch")
            self.assertIn('URL Chapter', chapter.content, "Content missing")

    def test_auto_title_from_html(self):
        """Test automatic title extraction from HTML / 测试从HTML自动提取标题"""
        html_string = '''<!DOCTYPE html>
<html>
<head><title>Auto Title</title></head>
<body>
    <h1>Content</h1>
</body>
</html>'''
        
        chapter = html2epub.create_chapter_from_string(html_string)
        
        self.assertEqual(chapter.title, 'Auto Title', "Auto-extracted title mismatch")


class TestImageHandling(unittest.TestCase):
    """Test image handling in chapters / 测试章节中的图片处理"""

    def test_chapter_with_images(self):
        """Test chapter with image tags / 测试包含图片标签的章节"""
        html_with_image = '''<!DOCTYPE html>
<html>
<head><title>Image Test</title></head>
<body>
    <h1>Chapter with Image</h1>
    <img src="https://example.com/image.jpg" alt="Test Image" />
    <p>Text after image</p>
</body>
</html>'''
        
        chapter = html2epub.create_chapter_from_string(
            html_with_image,
            title='Image Chapter'
        )
        
        # Chapter should be created even with images / 即使有图片也应该创建章节
        self.assertIsNotNone(chapter.content)
        self.assertIn('img', chapter.content.lower(), "Image tag missing")

    def test_local_image_copy(self):
        """Test copying local image / 测试复制本地图片"""
        # This would require actual image files, so we just verify the structure
        # 这需要实际的图片文件，所以我们只验证结构
        html_content = '<img src="local.jpg" alt="Local" />'
        chapter = html2epub.create_chapter_from_string(
            html_content,
            title='Local Image Test'
        )
        self.assertIsNotNone(chapter.content)


if __name__ == '__main__':
    unittest.main(verbosity=2)
