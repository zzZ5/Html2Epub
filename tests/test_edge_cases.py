#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Edge cases and error handling tests
边界情况和错误处理测试
"""

import sys
import os
import unittest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import html2epub


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and special scenarios / 测试边界情况和特殊场景"""

    def setUp(self):
        """Set up test environment / 设置测试环境"""
        self.test_output_dir = 'test_output'
        if not os.path.exists(self.test_output_dir):
            os.makedirs(self.test_output_dir)

    def test_very_long_title(self):
        """Test with very long title / 测试非常长的标题"""
        long_title = 'A' * 500  # 500 characters
        epub = html2epub.Epub(long_title)
        
        self.assertEqual(epub.title, long_title)

    def test_special_characters_in_content(self):
        """Test special characters in content / 测试内容中的特殊字符"""
        special_chars = '<p>Special chars: &lt; &gt; &amp; &quot; 中文 αβγ</p>'
        chapter = html2epub.create_chapter_from_string(
            special_chars,
            title='Special Chars'
        )
        
        self.assertIsNotNone(chapter.content)
        self.assertIn('Special chars:', chapter.content)

    def test_unicode_in_title(self):
        """Test unicode characters in title / 测试标题中的unicode字符"""
        unicode_title = '中文标题 Ελληνικά 日本語'
        epub = html2epub.Epub(unicode_title)
        
        self.assertEqual(epub.title, unicode_title)

    def test_nested_tags(self):
        """Test deeply nested tags / 测试深层嵌套标签"""
        nested_html = '''<div><div><div><div>
            <h1>Deep Level</h1>
            <p>Nested paragraph</p>
        </div></div></div></div>'''
        
        chapter = html2epub.create_chapter_from_string(
            nested_html,
            title='Nested'
        )
        
        self.assertIsNotNone(chapter.content)

    def test_many_chapters_performance(self):
        """Test with many chapters (performance check) / 测试大量章节(性能检查)"""
        epub = html2epub.Epub('Performance Test')
        
        chapter_count = 20
        for i in range(chapter_count):
            chapter = html2epub.create_chapter_from_string(
                f'<h1>Chapter {i+1}</h1><p>Content</p>',
                title=f'Chapter {i+1}'
            )
            epub.add_chapter(chapter)
        
        self.assertEqual(len(epub.chapters), chapter_count)
        # Create epub should work / 创建epub应该工作
        path = epub.create_epub(self.test_output_dir, 'performance')
        self.assertTrue(os.path.exists(path))

    def test_whitespace_only_chapter(self):
        """Test chapter with only whitespace / 测试只有空白字符的章节"""
        # Whitespace-only content still processes / 只有空白的内容仍然会处理
        html2epub.create_chapter_from_string(
            '   ',
            title='Whitespace'
        )

    def test_mixed_language_content(self):
        """Test mixed language content / 测试混合语言内容"""
        mixed_html = '''<h1>Mixed Language</h1>
        <p>English content 中文内容 日本語</p>
        <p>More mixed: Español Français Deutsch</p>'''
        
        chapter = html2epub.create_chapter_from_string(
            mixed_html,
            title='Mixed Language'
        )
        
        self.assertIn('English', chapter.content)
        self.assertIn('中文', chapter.content)
        self.assertIn('日本語', chapter.content)

    def test_html_entities(self):
        """Test HTML entities handling / 测试HTML实体处理"""
        entities_html = '''<p>Copyright &copy; 2024
        Trademark &trade;
        Euro &euro;
        Less than &lt;
        Greater than &gt;</p>'''
        
        chapter = html2epub.create_chapter_from_string(
            entities_html,
            title='Entities'
        )
        
        self.assertIsNotNone(chapter.content)

    def test_invalid_chapter_type(self):
        """Test adding invalid chapter type / 测试添加无效章节类型"""
        epub = html2epub.Epub('Type Test')
        
        with self.assertRaises(TypeError):
            epub.add_chapter('not a chapter object')

    def test_custom_epub_directory(self):
        """Test creating epub in custom directory / 测试在自定义目录创建epub"""
        custom_dir = 'custom_test_dir'
        if not os.path.exists(custom_dir):
            os.makedirs(custom_dir)
        
        try:
            epub = html2epub.Epub('Custom Dir Test', epub_dir=custom_dir)
            chapter = html2epub.create_chapter_from_string(
                '<h1>Test</h1><p>Content</p>',
                title='Test'
            )
            epub.add_chapter(chapter)
            path = epub.create_epub(self.test_output_dir, 'custom_dir')
            
            self.assertTrue(os.path.exists(path))
        finally:
            # Clean up / 清理
            if os.path.exists(custom_dir):
                import shutil
                shutil.rmtree(custom_dir)

    def test_table_structure(self):
        """Test HTML table structure / 测试HTML表格结构"""
        table_html = '''<table>
            <thead>
                <tr><th>Header 1</th><th>Header 2</th></tr>
            </thead>
            <tbody>
                <tr><td>Cell 1</td><td>Cell 2</td></tr>
                <tr><td>Cell 3</td><td>Cell 4</td></tr>
            </tbody>
        </table>'''
        
        chapter = html2epub.create_chapter_from_string(
            table_html,
            title='Table Test'
        )
        
        self.assertIn('<table', chapter.content.lower())

    def test_list_structure(self):
        """Test list structures / 测试列表结构"""
        list_html = '''
        <h1>Lists</h1>
        <ol>
            <li>Ordered item 1</li>
            <li>Ordered item 2</li>
        </ol>
        <ul>
            <li>Unordered item 1</li>
            <li>Unordered item 2</li>
        </ul>'''
        
        chapter = html2epub.create_chapter_from_string(
            list_html,
            title='Lists'
        )
        
        self.assertIn('<ol>', chapter.content)
        self.assertIn('<ul>', chapter.content)

    def test_epub_name_sanitization(self):
        """Test epub name sanitization / 测试epub名称清理"""
        epub = html2epub.Epub('Test / File: Special?Chars*')
        chapter = html2epub.create_chapter_from_string(
            '<p>Content</p>',
            title='Test'
        )
        epub.add_chapter(chapter)
        path = epub.create_epub(self.test_output_dir)
        
        # Should remove special characters / 应该移除特殊字符
        self.assertNotIn('/', path)
        self.assertNotIn(':', path)
        self.assertNotIn('?', path)
        self.assertTrue(os.path.exists(path))

    def test_no_title_fallback(self):
        """Test fallback when no title in HTML / 测试HTML中没有标题时的后备方案"""
        html_without_title = '<h1>Heading</h1><p>Content without title tag</p>'
        
        chapter = html2epub.create_chapter_from_string(html_without_title)
        
        # Should use default title / 应该使用默认标题
        self.assertEqual(chapter.title, 'Ebook Chapter')

    def test_multiple_images_in_chapter(self):
        """Test chapter with multiple images / 测试包含多张图片的章节"""
        multi_img_html = '''<h1>Multiple Images</h1>
        <img src="img1.jpg" />
        <p>Text between</p>
        <img src="img2.jpg" />
        <img src="img3.jpg" />'''
        
        chapter = html2epub.create_chapter_from_string(
            multi_img_html,
            title='Multiple Images'
        )
        
        # Should create chapter even with multiple images / 即使有多张图片也应该创建章节
        self.assertIsNotNone(chapter.content)


if __name__ == '__main__':
    unittest.main(verbosity=2)
