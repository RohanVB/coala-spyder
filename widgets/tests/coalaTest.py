import unittest
# todo: import run_coala
# from ..run_coala import UseCoala as coala

class TestOutput(unittest.TestCase):
    def test_start(self):
        self.assertEqual(1, 1)

def main():
    unittest.main()

# todo: test if it works properly with assertEqual and some testfile as input, expected output
# todo: create test on using spyder unittest plugin: https://github.com/spyder-ide/spyder-unittest
if __name__ == "__main__":
    main()