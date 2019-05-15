# Standard library imports
from __future__ import print_function, with_statement
import os.path as osp
import re
import sys
import time
import subprocess

"""
Third Party Imports
getopenfilename: for selecting python files to run linter on
QByteArray: used to store raw bytes
QProcess: for reading output
QTextCodec: used to retrieve text from bytes
Signal and slot: signal emitted when an event occurs, slot is a function response to that signal
QTWidgets: UI buttons, layout, etc,.
"""
from coalib.coala import main as coala
from qtpy.compat import getopenfilename
from qtpy.QtCore import QByteArray, QProcess, QTextCodec, Signal, Slot
from qtpy.QtWidgets import (QHBoxLayout, QLabel, QMessageBox, QTreeWidgetItem,
                            QVBoxLayout, QWidget)

"""
Local Imports

dependencies: Checks for missing dependencies
get_conf_path: gets path of results
get_translation: used for testing as standalone script 
pickle: pickled format
to_text_string: return text string
to_unicode_from_fs: return unicode string from file system encoding
create_toolbutton: creates QToolButton
get_cwd_or_home: get_cwd() or if cwd() is deleted, gets home directory
is_module_or_package: returns true if PATH is module or package
PythonModulesComboBox: QComboBox?
OneColumnTree: returns qtreewidget
TextEditor: Actual text editor with a "save and close" button
"""

from spyder import dependencies
from spyder.config.base import get_conf_path, get_translation
from spyder.py3compat import pickle, to_text_string
from spyder.utils import icon_manager as ima
from spyder.utils.encoding import to_unicode_from_fs
from spyder.utils.qthelpers import create_toolbutton
from spyder.utils.misc import getcwd_or_home
from spyder.widgets.comboboxes import (is_module_or_package,
                                       PythonModulesComboBox)
from spyder.widgets.onecolumntree import OneColumnTree
from spyder.plugins.variableexplorer.widgets.texteditor import TextEditor

try:
    _ = get_translation('coala', 'spyder_coala')
except KeyError as error:
    import gettext
    _ = gettext.gettext

locale_codec = QTextCodec.codecForLocale()
COALA_REQVER = '>=0.11.0'
COALA_VER = (subprocess.check_output(['coala', '--version']).decode('utf-8')).rstrip()
dependencies.add("coala", _("Static code analysis"),
                 required_version=COALA_REQVER, installed_version=COALA_VER)
