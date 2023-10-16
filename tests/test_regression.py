# SPDX-FileCopyrightText: 2023 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from scarfer.format.factory import FormatFactory
from scarfer.scan_interface import ScanReportReader
from scarfer.analyzer import Analyzer

CAIRO_REPORT_2 = "example-data/scancode/2.0.0/cairo-1.16.0-scan.json"
CAIRO_REPORT_3 = "example-data/scancode/3.0.0/cairo-1.16.0-scan.json"

class TestScancodeReader(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestScancodeReader, self).__init__(*args, **kwargs)

    def test_missing_license_2_0_0(self):
        """
        File cairo-1.16.0/util/show-events.c has no license
        make sure this is analyzed as  ['missing']
        In 3.0.0, scancode says: []
        """
        reader = ScanReportReader(CAIRO_REPORT_2)
        report = reader.read()
        analyzer = Analyzer(report)
        analyzer.apply_filters()
        analyzed_report = analyzer.report()
        for _file in analyzed_report['files']:
            if _file['path'] == 'cairo-1.16.0/util/show-events.c':
                _file_lic = _file['license']['expressions']
                self.assertEqual(_file_lic, ['missing'])
        
    def test_missing_license_3_0_0(self):
        """
        File cairo-1.16.0/util/show-events.c has no license
        make sure this is analyzed as  ['missing']
        In 3.0.0, scancode says: none
        """
        reader = ScanReportReader(CAIRO_REPORT_3)
        report = reader.read()
        analyzer = Analyzer(report)
        analyzer.apply_filters()
        analyzed_report = analyzer.report()
        for _file in analyzed_report['files']:
            if _file['path'] == 'cairo-1.16.0/util/show-events.c':
                _file_lic = _file['license']['expressions']
                self.assertEqual(_file_lic, ['missing'])
        

