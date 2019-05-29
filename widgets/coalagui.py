# Standard library imports
from __future__ import print_function, with_statement
import os.path as osp
import re
import sys
import subprocess
import ast

from qtpy.compat import getopenfilename
from qtpy.QtCore import QByteArray, QProcess, QTextCodec, Signal, Slot
from qtpy.QtWidgets import (QHBoxLayout, QLabel, QMessageBox, QTreeWidgetItem,
                            QVBoxLayout, QWidget)

from run_coala import UseCoala as coala
from spyder import dependencies
from spyder.config.base import get_conf_path, get_translation
from spyder.py3compat import pickle, to_text_string
from spyder.utils import icon_manager as ima
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

# todo: add coala-bears version
locale_codec = QTextCodec.codecForLocale()
COALA_REQVER = '>=0.11.0'
COALA_VER = (subprocess.check_output(['coala', '--version']).decode('utf-8')).rstrip()
dependencies.add("coala", _("Static code analysis"),
                 required_version=COALA_REQVER, installed_version=COALA_VER)


class ResultsTree(OneColumnTree):
    sig_edit_goto = Signal(str, int, str)

    def __init__(self, parent):
        OneColumnTree.__init__(self, parent)
        self.filename = None
        self.results = None
        self.data = None
        self.set_title('')

    def activated(self, item):
        """Double-click event"""
        data = self.data.get(id(item))
        if data is not None:
            fname, lineno = data
            self.sig_edit_goto.emit(fname, lineno, '')

    # def clicked(self, item):
    #     """Click event"""
    #     self.activated(item)

    def clear_results(self):
        self.clear()
        self.set_title('')

    def set_results(self, filename, results):
        self.filename = filename
        self.results = results
        self.refresh()

    def refresh(self):
        title = _('Results for ') + self.filename
        self.set_title(title)
        self.clear()
        self.data = {}
        if 'C:' in self.results:
            results = self.results
            result_vals = (_('coala'), ima.icon('convention'), results)
            title, icon, messages = result_vals
            title += ' (%d message%s)' % (len(messages),
                                          's' if len(messages) > 1 else '')
            title_item = QTreeWidgetItem(self, [title], QTreeWidgetItem.Type)
            if not messages:
                title_item.setDisabled(True)
            parent = title_item
            for lineno, charno, bearval, msg in messages['C:']:
                if lineno:
                    text = "(%d %d) %s: %s" % (int(lineno), int(charno), bearval, msg)

                else:
                    text = "%d : %s" % (int(lineno), msg)
                msg_item = QTreeWidgetItem(parent, [text], QTreeWidgetItem.Type)
                msg_item.setIcon(0, ima.icon('arrow'))
                self.data[id(msg_item)] = lineno



class CoalaWidget(QWidget):
    """
    coala Widget
    """
    DATAPATH = get_conf_path('coala.results')
    VERSION = ''
    redirect_stdio = Signal(bool)

    def __init__(self, parent, max_entries=100, options_button=None,
                 text_color=None, prevrate_color=None):
        QWidget.__init__(self, parent)
        self.setWindowTitle('coala')

        self.output = None
        self.error_output = None

        self.text_color = text_color
        self.prevrate_color = prevrate_color
        self.max_entries = max_entries
        self.rdata = []
        if osp.isfile(self.DATAPATH):
            try:
                data = pickle.loads(open(self.DATAPATH, 'rb').read())
                self.rdata = data[:]
            except (EOFError, ImportError):
                print('error!!')
                pass
        self.filecombo = PythonModulesComboBox(self)

        self.start_button = create_toolbutton(self, icon=ima.icon('run'),
                                    text=_("Analyze"),
                                    tip=_("Run analysis"),
                                    triggered=self.start, text_beside_icon=True)
        self.stop_button = create_toolbutton(self,
                                             icon=ima.icon('stop'),
                                             text=_("Stop"),
                                             tip=_("Stop current analysis"),
                                             text_beside_icon=True)
        self.filecombo.valid.connect(self.start_button.setEnabled)
        self.filecombo.valid.connect(self.show_data)

        browse_button = create_toolbutton(self, icon=ima.icon('fileopen'),
                               tip=_('Select Python file'),
                               triggered=self.select_file)

        self.ratelabel = QLabel()
        self.datelabel = QLabel()
        self.log_button = create_toolbutton(self, icon=ima.icon('log'),
                                    text=_("Output"),
                                    text_beside_icon=True,
                                    tip=_("Complete output"),
                                    triggered=self.show_log)
        self.treewidget = ResultsTree(self)

        hlayout1 = QHBoxLayout()
        hlayout1.addWidget(self.filecombo)
        hlayout1.addWidget(browse_button)
        hlayout1.addWidget(self.start_button)
        hlayout1.addWidget(self.stop_button)
        if options_button:
            hlayout1.addWidget(options_button)

        hlayout2 = QHBoxLayout()
        hlayout2.addWidget(self.ratelabel)
        hlayout2.addStretch()
        hlayout2.addWidget(self.datelabel)
        hlayout2.addStretch()
        hlayout2.addWidget(self.log_button)

        layout = QVBoxLayout()
        layout.addLayout(hlayout1)
        layout.addLayout(hlayout2)
        layout.addWidget(self.treewidget)
        self.setLayout(layout)

        self.process = None
        self.set_running_state(False)
        self.show_data()

        if self.rdata:
            self.remove_obsolete_items()
            self.filecombo.addItems(self.get_filenames())
            self.start_button.setEnabled(self.filecombo.is_valid())
        else:
            self.start_button.setEnabled(False)

    def analyze(self, filename):
        filename = to_text_string(filename) # filename is a QString instance
        self.kill_if_running()
        index, _data = self.get_data(filename)
        if index is None:
            self.filecombo.addItem(filename)
            self.filecombo.setCurrentIndex(self.filecombo.count()-1)
        else:
            self.filecombo.setCurrentIndex(self.filecombo.findText(filename))
        self.filecombo.selected()
        if self.filecombo.is_valid():
            self.start()

    @Slot()
    def select_file(self):
        self.redirect_stdio.emit(False)
        filename, _selfilter = getopenfilename(
                self, _("Select Python file"),
                getcwd_or_home(), _("Python files")+" (*.py ; *.pyw)")
        self.redirect_stdio.emit(True)
        if filename:
            self.analyze(filename)

    def remove_obsolete_items(self):
        """Removing obsolete items"""
        self.rdata = [(filename, data) for filename, data in self.rdata
                      if is_module_or_package(filename)]

    def get_filenames(self):
        return [filename for filename, _data in self.rdata]

    def get_data(self, filename):
        filename = osp.abspath(filename)
        for index, (fname, data) in enumerate(self.rdata):
            if fname == filename:
                return index, data
        else:
            return None, None

    def set_data(self, filename, data):
        filename = osp.abspath(filename)
        index, _data = self.get_data(filename)
        if index is not None:
            self.rdata.pop(index)
        self.rdata.insert(0, (filename, data))
        self.save()

    def save(self):
        while len(self.rdata) > self.max_entries:
            self.rdata.pop(-1)
        pickle.dump([self.VERSION]+self.rdata, open(self.DATAPATH, 'wb'), 2)

    @Slot()
    def show_log(self):
        if self.output:
            TextEditor(self.output, title=_("coala output"),
                       readonly=True, size=(700, 500)).exec_()

    @Slot()
    def start(self):
        filename = to_text_string(self.filecombo.currentText())

        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.SeparateChannels)
        self.process.setWorkingDirectory(osp.dirname(filename))
        self.process.readyReadStandardOutput.connect(self.read_output)
        self.process.readyReadStandardError.connect(
                                          lambda: self.read_output(error=True))
        self.process.finished.connect(lambda ec, es=QProcess.ExitStatus:
                                      self.finished(ec, es))
        self.stop_button.clicked.connect(self.process.kill)

        self.output = ''
        self.error_output = ''

        clver = COALA_VER
        if clver is not None:
            c_args = ['-m', 'run_coala']
        self.process.start(sys.executable, c_args)

        running = self.process.waitForStarted()
        self.set_running_state(running)
        if not running:
            QMessageBox.critical(self, _("Error"),
                                 _("Process failed to start"))

    def set_running_state(self, state=True):
        self.start_button.setEnabled(not state)
        self.stop_button.setEnabled(state)

    def read_output(self, error=False):
        if error:
            self.process.setReadChannel(QProcess.StandardError)
        else:
            self.process.setReadChannel(QProcess.StandardOutput)
        qba = QByteArray()
        while self.process.bytesAvailable():
            if error:
                qba += self.process.readAllStandardError()
            else:
                qba += self.process.readAllStandardOutput()
        text = to_text_string(locale_codec.toUnicode(qba.data()))
        if error:
            self.error_output += text
        else:
            self.output += text

    def finished(self, exit_code, exit_status):
        self.set_running_state(False)
        if not self.output:
            if self.error_output:
                QMessageBox.critical(self, _("Error"), self.error_output)
                print("coala error:\n\n" + self.error_output, file=sys.stderr)
            return

        results = {'C:': []}
        literal_dict = ast.literal_eval(self.output)
        line_numbers = []
        char_numbers = []
        bear_values = []
        msg_values = []
        for line in literal_dict['C']:
            for i in line:
                line_num = re.compile('(.+)~')
                val = line_num.findall(i)
                for line_nb in val:
                    if line_nb:
                        line_numbers.append(line_nb)
            for j in line:
                char_num = re.compile('(.*);')
                val = char_num.findall(j)
                for char_nm in val:
                    if char_nm:
                        char_numbers.append(char_nm)
            for k in line:
                bear_val = re.compile('(.*):')
                val = bear_val.findall(k)
                for bear_val in val:
                    if bear_val:
                        bear_values.append(bear_val)
            for m in line:
                msg_val = re.compile(':(.*)')
                val = msg_val.findall(m)
                for msg_val in val:
                    if msg_val:
                        msg_values.append(msg_val)

        item = list(zip(line_numbers, char_numbers, bear_values, msg_values))
        for i in item:
            results['C:'].append(i)
        filename = to_text_string(self.filecombo.currentText())
        self.set_data(filename, results)
        self.output = self.error_output + self.output
        self.show_data(justanalyzed=True)

    def kill_if_running(self):
        if self.process is not None:
            if self.process.state() == QProcess.Running:
                self.process.kill()
                self.process.waitForFinished()

    def show_data(self, justanalyzed=False):
        if not justanalyzed:
            self.output = None
        self.log_button.setEnabled(self.output is not None \
                                   and len(self.output) > 0)
        self.kill_if_running()
        filename = to_text_string(self.filecombo.currentText())
        if not filename:
            return

        _index, data = self.get_data(filename)
        if data is None:
            self.treewidget.clear_results()
        else:
            results = data
            self.treewidget.set_results(filename, results)


def test():
    """Run coala widget test"""
    from spyder.utils.qthelpers import qapplication
    app = qapplication(test_time=20)
    widget = CoalaWidget(None)
    widget.resize(640, 480)
    widget.show()
    widget.analyze(__file__)
    sys.exit(app.exec_())


if __name__ == '__main__':
    test()
