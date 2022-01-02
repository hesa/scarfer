import unittest

from scarfer.format.factory import FormatFactory

class TestFormatter(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestFormatter, self).__init__(*args, **kwargs)

    def test_formatter(self):
        formatter = FormatFactory.formatter("json")
        self.assertIsNotNone(formatter)
        formatter = FormatFactory.formatter("JSON")
        self.assertIsNotNone(formatter)

        
if __name__ == '__main__':
    unittest.main()
