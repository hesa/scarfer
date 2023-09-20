# SPDX-FileCopyrightText: 2023 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from scarfer.scan_interface import ScanReportReader
from scarfer.scan_interface import ScanReportException

class TestScanReader(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestScanReader, self).__init__(*args, **kwargs)

    def test_bad_reader(self):
        with self.assertRaises(ScanReportException):
            reader = ScanReportReader("bad-path")
            reader.read()


if __name__ == '__main__':
    unittest.main()
