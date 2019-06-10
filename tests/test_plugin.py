"""Tests for the plugin."""
import sys
import unittest

# local imports

sys.path.append('/Users/rohan/Documents/gsoc/spyder/spyder/plugins')
from coalaspyder.widgets.run_coala import UseCoala
from coalaspyder.widgets.coalagui import CoalaWidget


class TestRuncoala(unittest.TestCase):

    def setUp(self):
        self.file_val = x.specific_file()
        self.filename = x.output_to_diagnostics()
        self.output = x.give_output()

    def check_specific_file(self):
        pass

    def check_filename(self):
        pass

    def check_output_type(self):
        self.assertIs(self.output, tuple)


class Test(unittest.TestCase):

    def setUp(self):
        pass


if __name__ == '__main__':
    x = UseCoala
    y = CoalaWidget
    unittest.main()
