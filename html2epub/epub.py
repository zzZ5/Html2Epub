#!usr/bin/python3
# -*- coding: utf-8 -*-

# Included modules
import os
import shutil
import collections
import random
import string
import time
import tempfile
import imp
try:
    imp.find_module('lxml')
    lxml_module_exists = True
    import lxml.etree
    import lxml.html
    import lxml.html.builder
except ImportError:
    lxml_module_exists = False

# Third party modules
import jinja2

# Local modules
from . import chapter
from . import constants


class _Mimetype():
    """
    Epub的 Mimetype文件 类, 写入固定内容的 minetype文件 到epub.
    """

    def __init__(self, parent_directory):
        minetype_template = os.path.join(
            constants.EPUB_TEMPLATES_DIR, 'mimetype')
        shutil.copy(minetype_template,
                    os.path.join(parent_directory, 'mimetype'))


class _ContainerFile():
    """
    Epub的 Container文件 类, 写入固定内容的 container.xml文件到 epub.
    """

    def __init__(self, parent_directory):
        container_template = os.path.join(
            constants.EPUB_TEMPLATES_DIR, 'container.xml')
        shutil.copy(container_template,
                    os.path.join(parent_directory, 'container.xml'))


class _EpubFile():
    """
    用于将chapters写入Epub的类
    """

    def __init__(self, template_file, **non_chapter_parameters):
        self.content = ''
        self.file_name = ''
        self.template_file = template_file
        self.non_chapter_parameters = non_chapter_parameters

    def write(self, file_name):
        self.file_name = file_name
        with open(file_name, 'w', encoding="utf-8") as f:
            f.write(self.content)

    def _render_template(self, **variable_value_pairs):
        def read_template():
            with open(self.template_file, 'r', encoding="utf-8") as f:
                template = f.read()
            return jinja2.Template(template)
        template = read_template()
        rendered_template = template.render(variable_value_pairs)
        self.content = rendered_template

    def add_chapters(self, **parameter_lists):
        def check_list_lengths(lists):
            list_length = None
            for value in lists.values():
                # assert isinstance(value, list)
                if list_length is None:
                    list_length = len(value)
                else:
                    assert len(value) == list_length
        check_list_lengths(parameter_lists)
        template_chapter = collections.namedtuple('template_chapter',
                                                  parameter_lists.keys())
        chapters = [template_chapter(*items)
                    for items in zip(*parameter_lists.values())]
        self._render_template(chapters=chapters, **self.non_chapter_parameters)

    def get_content(self):
        return self.content


class TocHtml(_EpubFile):
    """
    Epub的 目录页面 类.
    """

    def __init__(self, template_file=os.path.join(constants.EPUB_TEMPLATES_DIR, 'toc.html'), **non_chapter_parameters):
        super(TocHtml, self).__init__(template_file, **non_chapter_parameters)

    def add_chapters(self, chapter_list):
        chapter_numbers = range(len(chapter_list))
        link_list = [str(n) + '.xhtml' for n in chapter_numbers]
        try:
            for c in chapter_list:
                t = type(c)
                assert type(c) == chapter.Chapter
        except AssertionError:
            raise TypeError('chapter_list items must be Chapter not %s',
                            str(t))
        chapter_titles = [c.title for c in chapter_list]
        super(TocHtml, self).add_chapters(title=chapter_titles,
                                          link=link_list)

    def get_content_as_element(self):
        if lxml_module_exists:
            root = lxml.html.fromstring(self.content.encode('utf-8'))
            return root
        else:
            raise NotImplementedError()


class TocNcx(_EpubFile):
    """
    Epub的 XML的导航控制文件(toc.ncx) 类 
    """

    def __init__(self,
                 template_file=os.path.join(
                     constants.EPUB_TEMPLATES_DIR, 'toc_ncx.xml'),
                 **non_chapter_parameters):
        super(TocNcx, self).__init__(template_file, **non_chapter_parameters)

    def add_chapters(self, chapter_list):
        id_list = range(len(chapter_list))
        play_order_list = [n + 1 for n in id_list]
        title_list = [c.title for c in chapter_list]
        link_list = [str(n) + '.xhtml' for n in id_list]
        super(TocNcx, self).add_chapters(**{'id': id_list,
                                            'play_order': play_order_list,
                                            'title': title_list,
                                            'link': link_list
                                            })

    def get_content_as_element(self):
        if lxml_module_exists:
            root = lxml.etree.fromstring(self.content.encode('utf-8'))
            return root
        else:
            raise NotImplementedError()


class ContentOpf(_EpubFile):
    """
    Epub的 .opf 类, 包含文件清单和文件阅读顺序等.
    """

    def __init__(self, title, creator='', language='', rights='', publisher='', uid='', date=time.strftime("%m-%d-%Y")):
        super(ContentOpf, self).__init__(os.path.join(constants.EPUB_TEMPLATES_DIR, 'opf.xml'),
                                         title=title,
                                         creator=creator,
                                         language=language,
                                         rights=rights,
                                         publisher=publisher,
                                         uid=uid,
                                         date=date)

    def add_chapters(self, chapter_list):
        id_list = range(len(chapter_list))
        link_list = [str(n) + '.xhtml' for n in id_list]
        imgs_list = [c.imgs for c in chapter_list]
        super(ContentOpf, self).add_chapters(
            **{'id': id_list, 'link': link_list, "imgs": imgs_list})

    def get_content_as_element(self):
        if lxml_module_exists:
            root = lxml.etree.fromstring(self.content.encode('utf-8'))
            return root
        else:
            raise NotImplementedError()


class Epub():
    """
    表示epub的类. 包含添加chapter和输出epub文件.

    Parameters:
        title (str): epub的标题.
        creator (Option[str]): epub的作者.
        language (Option[str]): epub的语言.
        rights (Option[str]): epub的版权.
        publisher (Option[str]): epub的出版商.
    """

    def __init__(self, title, creator='zzZ5', language='en', rights='', publisher='zzZ5', epub_dir=None):
        self._create_directories(epub_dir)
        self.chapters = []
        self.title = title
        try:
            assert title
        except AssertionError:
            raise ValueError('title cannot be empty string')
        self.creator = creator
        self.language = language
        self.rights = rights
        self.publisher = publisher
        self.uid = ''.join(random.choice(
            string.ascii_uppercase + string.digits) for _ in range(12))
        self.current_chapter_number = None
        self._increase_current_chapter_number()
        self.toc_html = TocHtml()
        self.toc_ncx = TocNcx()
        self.opf = ContentOpf(
            self.title, self.creator, self.language, self.rights, self.publisher, self.uid)
        self.minetype = _Mimetype(self.EPUB_DIR)
        self.container = _ContainerFile(self.META_INF_DIR)

    def _create_directories(self, epub_dir=None):
        """
        创建epub文件目录.
        """

        if epub_dir is None:
            self.EPUB_DIR = tempfile.mkdtemp()
        else:
            self.EPUB_DIR = epub_dir
        self.OEBPS_DIR = os.path.join(self.EPUB_DIR, 'OEBPS')
        self.META_INF_DIR = os.path.join(self.EPUB_DIR, 'META-INF')
        self.LOCAL_IMAGE_DIR = 'images'
        self.IMAGE_DIR = os.path.join(self.OEBPS_DIR, self.LOCAL_IMAGE_DIR)
        os.makedirs(self.OEBPS_DIR)
        os.makedirs(self.META_INF_DIR)
        os.makedirs(self.IMAGE_DIR)

    def _increase_current_chapter_number(self):
        """
        增长当前章节序号.
        """

        if self.current_chapter_number is None:
            self.current_chapter_number = 0
        else:
            self.current_chapter_number += 1
        self.current_chapter_id = str(self.current_chapter_number)
        self.current_chapter_path = ''.join(
            [self.current_chapter_id, '.xhtml'])

    def add_chapter(self, c):
        """
        向epub中添加chapter. 创建各章节的xhtml文件.

        Parameters:
            c (Chapter): 要添加的chapter.
        Raises:
            TypeError: 如果添加的章节类型不对触发此 Error.
        """
        try:
            assert type(c) == chapter.Chapter
        except AssertionError:
            raise TypeError('chapter must be of type Chapter')
        chapter_file_output = os.path.join(
            self.OEBPS_DIR, self.current_chapter_path)
        c._replace_images_in_chapter(self.OEBPS_DIR)
        c.write(chapter_file_output)
        self._increase_current_chapter_number()
        self.chapters.append(c)

    def create_epub(self, output_directory, epub_name=None):
        """
        从该对象中创建epub文件.

        Parameters:
            output_directory (str): Directory to output the epub file to
            epub_name (Option[str]): The file name of your epub. This should not contain
                .epub at the end. If this argument is not provided, defaults to the title of the epub.
        """
        def createTOCs_and_ContentOPF():
            """
            创建目录和opf文件等.
            """

            for epub_file, name in ((self.toc_html, 'toc.html'), (self.toc_ncx, 'toc.ncx'), (self.opf, 'content.opf'),):
                epub_file.add_chapters(self.chapters)
                epub_file.write(os.path.join(self.OEBPS_DIR, name))

        def create_zip_archive(epub_name):
            try:
                assert isinstance(
                    epub_name, str) or epub_name is None
            except AssertionError:
                raise TypeError('epub_name must be string or None')
            if epub_name is None:
                epub_name = self.title
            epub_name = ''.join(
                [c for c in epub_name if c.isalpha() or c.isdigit() or c == ' ']).rstrip()
            epub_name_with_path = os.path.join(output_directory, epub_name)
            try:
                os.remove(os.path.join(epub_name_with_path, '.zip'))
            except OSError:
                pass
            shutil.make_archive(epub_name_with_path, 'zip', self.EPUB_DIR)
            return epub_name_with_path + '.zip'

        def turn_zip_into_epub(zip_archive):
            epub_full_name = zip_archive.strip('.zip') + '.epub'
            try:
                os.remove(epub_full_name)
            except OSError:
                pass
            os.rename(zip_archive, epub_full_name)
            return epub_full_name
        createTOCs_and_ContentOPF()
        epub_path = turn_zip_into_epub(create_zip_archive(epub_name))
        return epub_path
