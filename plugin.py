# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
# (see spyder/__init__.py for details)


# Standard library imports
import os.path as osp

# Third party imports
from qtpy.QtCore import Slot
from qtpy.QtWidgets import QInputDialog, QVBoxLayout

# Local imports
from spyder.config.base import _
from spyder.config.gui import is_dark_interface
from spyder.api.plugins import SpyderPluginWidget
from spyder.utils import icon_manager as ima
from spyder.utils.programs import is_module_installed
from spyder.utils.qthelpers import create_action, MENU_SEPARATOR

# imports from coala
from spyder.plugins.coalaspyder.widgets.confpage import CoalaConfigPage
from spyder.plugins.coalaspyder.widgets.coalagui import CoalaWidget

if is_dark_interface():
    MAIN_TEXT_COLOR = 'white'
    MAIN_PREVRATE_COLOR = 'white'
else:
    MAIN_TEXT_COLOR = '#444444'
    MAIN_PREVRATE_COLOR = '#666666'


class Coala(SpyderPluginWidget):

    CONF_SECTION = 'coala'
    CONFIGWIDGET_CLASS = CoalaConfigPage

    def __init__(self, parent=None):
        SpyderPluginWidget.__init__(self, parent)

        max_entries = self.get_option('max_entries', 50)
        self.coala = CoalaWidget(self, max_entries=max_entries,
                                   options_button=self.options_button,
                                   text_color=MAIN_TEXT_COLOR,
                                   prevrate_color=MAIN_PREVRATE_COLOR)

        layout = QVBoxLayout()
        layout.addWidget(self.coala)
        self.setLayout(layout)

        # Add history_action to treewidget context menu
        history_action = create_action(self, _("History..."),
                                       None, ima.icon('history'),
                                       _("Set history maximum entries"),
                                       triggered=self.change_history_depth)
        self.coala.treewidget.common_actions += (None, history_action)

        # Initialize plugin
        self.initialize_plugin()

    # ------ SpyderPluginWidget API --------------------------------------------
    def get_plugin_title(self):
        """Return widget title"""
        return _("coala")

    def get_plugin_icon(self):
        """Return widget icon"""
        path = osp.join(self.PLUGIN_PATH, self.IMG_PATH)
        return ima.icon('coalaspyder', icon_path=path)

    def get_focus_widget(self):
        """
        Return the widget to give focus to when
        this plugin's dockwidget is raised on top-level
        """
        return self.coala.treewidget

    def get_plugin_actions(self):
        """Return a list of actions related to plugin"""
        return self.coala.treewidget.get_menu_actions()

    def on_first_registration(self):
        """Action to be performed on first plugin registration"""
        self.main.tabify_plugins(self.main.help, self)
        self.dockwidget.hide()

    def register_plugin(self):
        """Register plugin in Spyder's main window"""
        self.coala.treewidget.sig_edit_goto.connect(self.main.editor.load)
        self.coala.redirect_stdio.connect(
            self.main.redirect_internalshell_stdio)
        self.main.add_dockwidget(self)

        coala_act = create_action(self, _("Run coala"),
                                   triggered=self.run_coala)
        coala_act.setEnabled(is_module_installed('coala'))
        self.register_shortcut(coala_act, context="Coala",
                               name="Run analysis")

        self.main.source_menu_actions += [MENU_SEPARATOR, coala_act]
        self.main.editor.pythonfile_dependent_actions += [coala_act]

    def refresh_plugin(self):
        """Refresh coala widget"""
        self.coala.remove_obsolete_items()

    def closing_plugin(self, cancelable=False):
        """Perform actions before parent main window is closed"""
        return True

    def apply_plugin_settings(self, options):
        """Apply configuration file's plugin settings"""
        # The history depth option will be applied at
        # next Spyder startup, which is soon enough
        pass

    # ------ Public API --------------------------------------------------------
    @Slot()
    def change_history_depth(self):
        "Change history max entries"""
        depth, valid = QInputDialog.getInt(self, _('History'),
                                           _('Maximum entries'),
                                           self.get_option('max_entries'),
                                           10, 10000)
        if valid:
            self.set_option('max_entries', depth)

    @Slot()
    def run_coala(self):
        """Run coala code analysis"""
        if (self.get_option('save_before', True)
                and not self.main.editor.save()):
            return
        self.switch_to_plugin()
        self.analyze(self.main.editor.get_current_filename())

    def analyze(self, filename):
        """Reimplement analyze method"""
        if self.dockwidget and not self.ismaximized:
            self.dockwidget.setVisible(True)
            self.dockwidget.setFocus()
            self.dockwidget.raise_()
        self.coala.analyze(filename)
