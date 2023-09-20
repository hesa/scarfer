# SPDX-FileCopyrightText: 2023 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from scarfer.scan_interface import ScanReportReader
from scarfer.analyzer import ScanReportFilter
from scarfer.analyzer import ScanReportFilterType
from scarfer.analyzer import Analyzer

CAIRO_REPORT_0 = "example-data/scancode/no-format/cairo-1.16.0-scan.json"
CAIRO_REPORT_1 = "example-data/scancode/1.0.0/cairo-1.16.0-scan.json"
CAIRO_REPORT_2 = "example-data/scancode/2.0.0/cairo-1.16.0-scan.json"

class TestScancodeReader_0(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestScancodeReader_0, self).__init__(*args, **kwargs)
        self._setup(CAIRO_REPORT_0)

    def _setup(self, report):
        self.reader = ScanReportReader(report)
        normalized_report = self.reader.read()
        self.analyzer = Analyzer(normalized_report)
        self.analyzer.apply_filters()
        self.data = self.analyzer.report()
        self.before_count = len(self.data['files'])
        self.assertEqual(self.before_count, 4686)

    def test_license_filter(self):
        # filter in files with license with "x11"
        license_filter = ScanReportFilter("x11", ScanReportFilterType.LICENSE)
        # apply filter
        self.analyzer.apply_filters([license_filter])

        filtered_data = self.analyzer.report()

        self.assertIsNotNone(filtered_data)
        after_count = len(filtered_data['files'])
        self.assertEqual(after_count, 309)

    def test_copyright_filter(self):
        # filter in files with copyright with "laar"
        copyright_filter = ScanReportFilter("laar", ScanReportFilterType.COPYRIGHT)
        # apply filter
        self.analyzer.apply_filters([copyright_filter])

        filtered_data = self.analyzer.report()

        self.assertIsNotNone(filtered_data)
        after_count = len(filtered_data['files'])
        self.assertEqual(after_count, 9)

    def test_file_filter(self):

        # filter in files with path with "cairo-xcb"
        file_filter = ScanReportFilter("cairo-xcb")

        # apply filter
        self.analyzer.apply_filters([file_filter])
        filtered_data = self.analyzer.report()

        self.assertIsNotNone(filtered_data)
        after_count = len(filtered_data['files'])
        self.assertEqual(after_count, 13)

    def test_file_license_filters(self):

        # filter in files with license with "x11"
        license_filter = ScanReportFilter("x11", ScanReportFilterType.LICENSE)
        # filter in files with path with "cairo-xcb"
        file_filter = ScanReportFilter("cairo-xcb")

        # apply filter
        self.analyzer.apply_filters([file_filter, license_filter])
        filtered_data = self.analyzer.report()

        self.assertIsNotNone(filtered_data)
        after_count = len(filtered_data['files'])
        self.assertEqual(after_count, 1)

    def test_file_copyright_filters(self):

        # filter in files with copyright with "laar" (9 of them)
        copyright_filter = ScanReportFilter("laar", ScanReportFilterType.COPYRIGHT)
        # filter out files with path with "test" (6 of the 9)
        file_filter = ScanReportFilter("test")

        # apply filter
        self.analyzer.apply_filters([copyright_filter], [file_filter])

        filtered_data = self.analyzer.report()

        self.assertIsNotNone(filtered_data)
        after_count = len(filtered_data['files'])
        self.assertEqual(after_count, 3)

    def test_file_exclude(self):

        # filter out files with license with "x11"
        license_filter = ScanReportFilter("x11-keith", ScanReportFilterType.LICENSE)

        # apply filter
        self.analyzer.apply_filters([], [license_filter])
        filtered_data = self.analyzer.report()

        self.assertIsNotNone(filtered_data)
        after_count = len(filtered_data['files'])

        # $ PYTHONPATH=. ./scarfer/__main__.py example-data/cairo-1.16.0-scan.json -l | grep -v x11-keith  | grep ^cairo | wc -l
        # 4378
        self.assertEqual(after_count, 4378)

    def test_license_exclude(self):

        # filter out files with path with "test"
        file_filter = ScanReportFilter("/test")

        # apply filter
        self.analyzer.apply_filters([], [file_filter])
        filtered_data = self.analyzer.report()

        self.assertIsNotNone(filtered_data)
        after_count = len(filtered_data['files'])

        # $ PYTHONPATH=. ./scarfer/__main__.py example-data/cairo-1.16.0-scan.json -l | grep -v /test | grep ^cairo | wc -l
        # 745
        self.assertEqual(after_count, 745)

    def test_file_license_exclude(self):

        # filter out files with license with "x11"
        license_filter = ScanReportFilter("x11-keith", ScanReportFilterType.LICENSE)

        # filter out files with path with "test"
        file_filter = ScanReportFilter("/test")

        # apply filter
        self.analyzer.apply_filters([], [file_filter, license_filter])
        filtered_data = self.analyzer.report()

        self.assertIsNotNone(filtered_data)
        after_count = len(filtered_data['files'])

        # $ PYTHONPATH=. ./scarfer/__main__.py example-data/cairo-1.16.0-scan.json -l | grep -v /test | grep -v x11-keith  | grep ^cairo | wc -l
        # 683
        self.assertEqual(after_count, 683)

class TestScancodeReader_1(TestScancodeReader_0):

    def __init__(self, *args, **kwargs):
        super(TestScancodeReader_1, self).__init__(*args, **kwargs)
        self._setup(CAIRO_REPORT_1)

class TestScancodeReader_2(TestScancodeReader_0):

    def __init__(self, *args, **kwargs):
        super(TestScancodeReader_2, self).__init__(*args, **kwargs)
        self._setup(CAIRO_REPORT_2)


if __name__ == '__main__':
    unittest.main()
