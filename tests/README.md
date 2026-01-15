# Test Documentation / 测试文档

## Running Tests / 运行测试

### Run All Tests / 运行所有测试
```bash
python run_tests.py
```

### Run Specific Test Module / 运行特定测试模块
```bash
# Basic functionality tests / 基本功能测试
python run_tests.py -m basic

# HTML cleaning tests / HTML清理测试
python run_tests.py -m cleaning

# Edge cases tests / 边界情况测试
python run_tests.py -m edge
```

### Using unittest directly / 直接使用unittest
```bash
# Run all tests / 运行所有测试
python -m unittest discover -s tests -v

# Run specific test file / 运行特定测试文件
python -m unittest tests.test_basic -v
python -m unittest tests.test_html_cleaning -v
python -m unittest tests.test_edge_cases -v
```

## Test Structure / 测试结构

```
tests/
├── __init__.py                # Test package initialization / 测试包初始化
├── test_basic.py              # Basic epub creation tests / 基本epub创建测试
│   ├── TestEpubBasic         # Epub class tests / Epub类测试
│   ├── TestChapterFactory    # Chapter creation tests / 章节创建测试
│   └── TestImageHandling    # Image handling tests / 图片处理测试
├── test_html_cleaning.py      # HTML cleaning tests / HTML清理测试
│   ├── TestHTMLCleaning      # HTML clean function tests / HTML clean函数测试
│   └── TestFragmentWrapping  # Fragment wrapping tests / 片段包装测试
└── test_edge_cases.py         # Edge cases and error handling / 边界情况和错误处理
    └── TestEdgeCases        # Edge case tests / 边界情况测试
```

## Test Coverage / 测试覆盖

### Test Categories / 测试分类

1. **Basic Functionality / 基本功能** (10 tests)
   - Create epub from string / 从字符串创建epub
   - Create epub from file / 从文件创建epub
   - Create epub from URL / 从URL创建epub
   - Multiple chapters / 多章节
   - Metadata handling / 元数据处理

2. **HTML Cleaning / HTML清理** (15 tests)
   - Tag filtering / 标签过滤
   - Attribute filtering / 属性过滤
   - Special character handling / 特殊字符处理
   - XHTML conversion / XHTML转换

3. **Edge Cases / 边界情况** (15 tests)
   - Unicode handling / Unicode处理
   - Special characters / 特殊字符
   - Performance / 性能
   - Error handling / 错误处理

## Test Output / 测试输出

All test outputs are saved to: / 所有测试输出保存到：
```
test_output/
```

## Continuous Integration / 持续集成

### GitHub Actions Example / GitHub Actions示例
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Run tests
      run: |
        python run_tests.py
```

## Writing New Tests / 编写新测试

### Test Template / 测试模板

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import unittest

# Add parent directory to path / 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import html2epub


class TestNewFeature(unittest.TestCase):
    """Test new feature / 测试新功能"""
    
    def setUp(self):
        """Set up test environment / 设置测试环境"""
        self.test_output_dir = 'test_output'
        if not os.path.exists(self.test_output_dir):
            os.makedirs(self.test_output_dir)
    
    def test_something(self):
        """Test something specific / 测试特定功能"""
        # Arrange / 准备
        epub = html2epub.Epub('Test')
        
        # Act / 执行
        chapter = html2epub.create_chapter_from_string(
            '<h1>Test</h1><p>Content</p>',
            title='Test Chapter'
        )
        epub.add_chapter(chapter)
        
        # Assert / 断言
        self.assertIsNotNone(chapter.content)
        self.assertEqual(chapter.title, 'Test Chapter')


if __name__ == '__main__':
    unittest.main(verbosity=2)
```

## Best Practices / 最佳实践

1. **Use descriptive names / 使用描述性名称**
   - Good: `test_create_epub_from_string`
   - Bad: `test_1`

2. **Test both success and failure cases / 测试成功和失败情况**
   - Normal operation / 正常操作
   - Edge cases / 边界情况
   - Error conditions / 错误条件

3. **Clean up test files / 清理测试文件**
   - Use `setUp` and `tearDown` for setup/cleanup / 使用setUp和tearDown进行设置/清理
   - Or keep test output for inspection / 或保留测试输出以便检查

4. **Write bilingual comments / 编写双语注释**
   - ```python
     """Test creating epub from HTML string / 测试从HTML字符串创建epub"""
     ```
