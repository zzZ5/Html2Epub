#!usr/bin/python3
# -*- coding: utf-8 -*-

# import from python standard library
import os
import shutil
import collections
import random
import string
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
# import from other modules
import jinja2

# import from local modules
import chapter
from .constants import *


class _Minetype():

    def __init__(self, parent_directory):
        minetype_template = os.path.join(EPUB_TEMPLATES_DIR, 'minetype.txt')
        shutil.copy(minetype_template,
                    os.path.join(parent_directory, 'minetype.txt'))


class _ContainerFile():

    def __init__(self, parent_directory):
        container_template = os.path.join(EPUB_TEMPLATES_DIR, 'container.xml')
        shutil.copy(container_template,
                    os.path.join(parent_directory, 'container.xml'))


class _EpubFile():
    """
    Class that used to write chapters to an epub.
    """

    def __init__(self, template_file, **non_chapter_parameters):
        self.content = ''
        self.file_name = ''
        self.template_file = template_file
        self.non_chapter_parameters = non_chapter_parameters

    def write(self, file_name):
        self.file_name = file_name
        with open(file_name, 'wb', encoding="utf-8") as f:
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
                assert isinstance(value, list)
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

    def __init__(self, template_file=os.path.join(EPUB_TEMPLATES_DIR, 'toc.html'), **non_chapter_parameters):
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

    def __init__(self,
                 template_file=os.path.join(EPUB_TEMPLATES_DIR, 'toc_ncx.xml'),
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
                                            'link': link_list})

    def get_content_as_element(self):
        if lxml_module_exists:
            root = lxml.etree.fromstring(self.content.encode('utf-8'))
            return root
        else:
            raise NotImplementedError()


class ContentOpf(_EpubFile):

    def __init__(self, title, creator='', language='', rights='', publisher='', uid='', date=time.strftime("%m-%d-%Y")):
        super(ContentOpf, self).__init__(os.path.join(EPUB_TEMPLATES_DIR, 'opf.xml'),
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
        super(ContentOpf, self).add_chapters(
            **{'id': id_list, 'link': link_list})

    def get_content_as_element(self):
        if lxml_module_exists:
            root = lxml.etree.fromstring(self.content.encode('utf-8'))
            return root
        else:
            raise NotImplementedError()


class Epub():
    """
    Class representing an epub. Add chapters to this and then output your ebook
    as an epub file.

    Args:
        title (str): The title of the epub.
        creator (Option[str]): The creator of your epub. By default this is
            pypub.
        language (Option[str]): The language of your epub.
        rights (Option[str]): The rights of your epub.
        publisher (Option[str]): The publisher of your epub. By default this
            is pypub.
    """

    def __init__(self, title, creator='zzZ5', language='zh', rights='', publisher='zzZ5', epub_dir=None):
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
        # self.current_chapter_number = Nones
        # self._increase_current_chapter_number()
        self.toc_html = TocHtml()
        self.toc_ncx = TocNcx()
        self.opf = ContentOpf(
            self.title, self.creator, self.language, self.rights, self.publisher, self.uid)
        self.minetype = _Minetype(self.EPUB_DIR)
        self.container = _ContainerFile(self.META_INF_DIR)

    def _create_directories(self, epub_dir=None):
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
