import sys
import unittest

sys.path.append('..')

from widgets.run_coala import UseCoala  # noqa

'""Tests for run_coala.py .""'


class TestRuncoala(unittest.TestCase):

    def setUp(self):
        x = UseCoala
        self.file_val = x.specific_file('../widgets', '*.py')
        self.final_list, self.filename = x.output_to_diagnostics()
        self.output = x.give_output()

    def test_log(self):
        pass

    def test_specific_file(self):
        pass

    def test_output_to_diagnostics(self):
        self.assertIs(type(self.final_list), list)
        self.assertIs(type(self.filename), str)

    def test_give_output(self):
        self.assertIs(type(self.output), list)
        self.assertIs(type(self.output[0]), tuple)


if __name__ == '__main__':
    unittest.main()
