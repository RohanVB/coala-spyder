"""Tests for the plugin."""

# Standard library imports
import json
import os
import os.path as osp
import shutil
import tempfile

# Third-party library imports
from flaky import flaky
import pytest
import requests
from qtpy.QtWebEngineWidgets import WEBENGINE
from qtpy.QtCore import Qt, QTimer
from qtpy.QtWidgets import QFileDialog, QApplication, QLineEdit
from spyder.config.base import get_home_dir

# local imports

from coalaspyder import plugin


# =============================================================================
# Fixtures
# =============================================================================
@pytest.fixture
def notebook(qtbot):
    """Set up the Notebook plugin."""
    coala_plugin = plugin(None, testing=True)
    qtbot.addWidget(coala_plugin)
    coala_plugin.create_new_client()
    coala_plugin.show()
    return coala_plugin

@pytest.fixture(scope='module')
def tmpdir_under_home():
    """Create a temporary directory under the home dir."""
    tmpdir = tempfile.mkdtemp(dir=get_home_dir())
    yield tmpdir
    print('rmtree', tmpdir)
    shutil.rmtree(tmpdir)


if __name__ == "__main__":
    pytest.main()
