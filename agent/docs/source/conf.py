# coding=utf-8
import os
import shlex
import sphinx_rtd_theme
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import comnsense_agent

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.todo',
    'sphinx.ext.mathjax',
    'sphinx.ext.ifconfig',
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']

source_suffix = '.rst'

master_doc = 'index'

project = u'comnsense-agent'
copyright = comnsense_agent.__copyright__
author = comnsense_agent.__author__

primary_domain = 'py'
default_role = 'any'

autodoc_member_order = "bysource"
autoclass_content = "both"

version = comnsense_agent.__version__
release = comnsense_agent.__version__

language = "en"

exclude_patterns = []

pygments_style = 'sphinx'

todo_include_todos = True


html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

html_static_path = ['_static']

htmlhelp_basename = 'comnsense-agentdoc'
