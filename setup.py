from setuptools import setup

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='html2epub',
    version='1.3',
    author='zzZ5',
    author_email='baoju_liu@foxmail.com',
    description='将 html链接, html文件 或 html文本 转换成 epub文件.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/zzZ5/Html2Epub',
    packages=['html2epub'],
    package_data={'html2epub': ['epub_templates/*', ]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'beautifulsoup4>=4.7.1',
        'jinja2>=2.10.1',
        'lxml>=4.3.4',
        'requests>=2.22.0',
    ]
)
