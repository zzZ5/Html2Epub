#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test runner for html2epub
html2epub测试运行器
"""

import sys
import os
import unittest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import test modules / 导入测试模块
from tests import test_basic
from tests import test_html_cleaning
from tests import test_edge_cases


def run_all_tests():
    """Run all tests / 运行所有测试"""
    print("=" * 70)
    print("Html2Epub Test Suite / Html2Epub测试套件")
    print("=" * 70)
    print()
    
    # Create test suite / 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test modules / 添加测试模块
    suite.addTests(loader.loadTestsFromModule(test_basic))
    suite.addTests(loader.loadTestsFromModule(test_html_cleaning))
    suite.addTests(loader.loadTestsFromModule(test_edge_cases))
    
    # Run tests / 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary / 打印摘要
    print()
    print("=" * 70)
    print("Test Summary / 测试摘要")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)
    
    # Return exit code / 返回退出码
    return 0 if result.wasSuccessful() else 1


def run_specific_test(test_module):
    """Run specific test module / 运行特定测试模块"""
    print(f"Running {test_module.__name__}...")
    print("-" * 70)
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(test_module)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Run html2epub tests / 运行html2epub测试',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '-m', '--module',
        type=str,
        choices=['basic', 'cleaning', 'edge', 'all'],
        default='all',
        help='Test module to run / 要运行的测试模块 (default: all)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output / 详细输出'
    )
    
    args = parser.parse_args()
    
    # Ensure test output directory exists / 确保测试输出目录存在
    if not os.path.exists('test_output'):
        os.makedirs('test_output')
    
    # Run tests / 运行测试
    if args.module == 'basic':
        sys.exit(run_specific_test(test_basic))
    elif args.module == 'cleaning':
        sys.exit(run_specific_test(test_html_cleaning))
    elif args.module == 'edge':
        sys.exit(run_specific_test(test_edge_cases))
    else:
        sys.exit(run_all_tests())
