# -*- coding: utf-8 -*-
import sys
import os
import shlex

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
print sys.path

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
copyright = u'2015, Comnsense Team'
author = u'Comnsense Team'

primary_domain = 'py'
default_role = 'py:obj'

autodoc_member_order = "bysource"
autoclass_content = "both"

version = '0.0.1'
release = '0.0.1'

language = None

exclude_patterns = []

pygments_style = 'sphinx'

todo_include_todos = True


html_theme = 'alabaster'

html_static_path = ['_static']

htmlhelp_basename = 'comnsense-agentdoc'

latex_elements = {
# The paper size ('letterpaper' or 'a4paper').
#'papersize': 'letterpaper',

# The font size ('10pt', '11pt' or '12pt').
#'pointsize': '10pt',

# Additional stuff for the LaTeX preamble.
#'preamble': '',

# Latex figure (float) alignment
#'figure_align': 'htbp',
}

latex_documents = [
  (master_doc, 'comnsense-agent.tex', u'comnsense-agent Documentation',
   u'Comnsense Team', 'manual'),
]

# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'comnsense-agent', u'comnsense-agent Documentation',
     [author], 1)
]

texinfo_documents = [
  (master_doc, 'comnsense-agent', u'comnsense-agent Documentation',
   author, 'comnsense-agent', 'One line description of project.',
   'Miscellaneous'),
]
