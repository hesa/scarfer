# SPDX-FileCopyrightText: 2023 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
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
        In 2.0.0, scancode says: []
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

    def test_matching_license_2_0_0(self):
        """
        File cairo-1.16.0/util/cairo-script/cairo-script-file.c has two licenses identified
        """
        reader = ScanReportReader(CAIRO_REPORT_2)
        report = reader.read()
        analyzer = Analyzer(report)
        analyzer.apply_filters()
        analyzed_report = analyzer.report()
        for _file in analyzed_report['files']:
            if _file['path'] == 'cairo-1.16.0/util/cairo-script/cairo-script-file.c':
                match_count = len(_file['license']['matches'])
                self.assertEqual(2, match_count)

                file_lic = _file['license']['expressions']
                self.assertEqual(['lgpl-2.1 OR mpl-1.1'], file_lic)

    def test_matching_license_3_0_0(self):
        """
        File cairo-1.16.0/util/cairo-script/cairo-script-file.c has THREE licenses identified
        """
        reader = ScanReportReader(CAIRO_REPORT_3)
        report = reader.read()
        analyzer = Analyzer(report)
        analyzer.apply_filters()
        analyzed_report = analyzer.report()
        for _file in analyzed_report['files']:
            if _file['path'] == 'cairo-1.16.0/util/cairo-script/cairo-script-file.c':
                match_count = len(_file['license']['matches'])
                self.assertEqual(3, match_count)

                file_lic = _file['license']['expressions']
                # THIS EXPRESSION SHOULD BE WITH AN "AND" Until
                # https://github.com/nexB/scancode-toolkit/issues/3523
                # is fixed, we need to keep it this way When the
                # scancode bug is fixed, rescan and replace current
                # scan report
                self.assertEqual(['lgpl-2.1 AND mpl-1.1'], file_lic)
