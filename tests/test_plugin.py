"""Tests for the plugin."""
import sys
import unittest

# local imports

sys.path.append('/Users/rohan/Documents/gsoc/spyder/spyder/plugins')
from coalaspyder.widgets.run_coala import UseCoala
# from coalaspyder.widgets.coalagui import CoalaWidget


class TestRuncoala(unittest.TestCase):

    def setUp(self):
        x = UseCoala
        self.file_val = x.specific_file('/Users/rohan/Documents/gsoc/spyder/spyder/plugins/coalaspyder/widgets', '*.py')
        self.filename = x.output_to_diagnostics()
        self.output = x.give_output()

    def test_specific_file(self):
        pass

    def test_filename(self):
        pass

    def test_type(self):
        self.assertIs(self.output, tuple)


class Test(unittest.TestCase):

    def setUp(self):
        pass


if __name__ == '__main__':
    unittest.main()
