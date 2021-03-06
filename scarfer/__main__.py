#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

from argparse import RawTextHelpFormatter
import argparse
import os

from scarfer.format.factory import FormatFactory
from scarfer.scan_interface import ScanReportReader
from scarfer.scan_interface import ScanReportException
from scarfer.format.interface import Settings
from scarfer.filter_utils import create_filters
from scarfer.config import scarfer_version
from scarfer.config import scarfer_name

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

PROGRAM_NAME = scarfer_name
PROGRAM_DESCRIPTION = "Source code scan report file reporter reads scan reports and outputs selected information about filtered files"
PROGRAM_URL = "https://github.com/hesa/scarfer"
PROGRAM_EXAMPLES = "   Coming soon."
BUG_URL = "https://github.com/hesa/scarfer/issues"
PROGRAM_COPYRIGHT = "(c) 2021 Henrik Sandklef<hesa@sandklef.com>"
PROGRAM_LICENSE = "GPL-3.0-or-later"
PROGRAM_AUTHOR = "Henrik Sandklef"
PROGRAM_SUPPORTED_FORMATS = "   * Scancode Output Format version 1.0.0\n   * Scaancode Toolkit, version 21 and upwards\n"
PROGRAM_ATTRIBUTION = ""
PROGRAM_SEE_ALSO = ""

OUTPUT_FORMAT_JSON = "JSON"
OUTPUT_FORMAT_TEXT = "text"
OUTPUT_FORMAT_YAML = "text"
OUTPUT_FORMATS = [ OUTPUT_FORMAT_JSON, OUTPUT_FORMAT_TEXT, OUTPUT_FORMAT_YAML ]

DATE_FMT = '%Y-%m-%d'

def parse():

    description = "NAME\n  " + PROGRAM_NAME + "\n\n"
    description = description + "DESCRIPTION\n  " + PROGRAM_DESCRIPTION + "\n\n"
    
    epilog = ""
    epilog = epilog + "EXAMPLES\n\n" + PROGRAM_EXAMPLES + "\n\n"
    epilog = epilog + "SUPPORTED SCAN REPORT FORMATS\n" + PROGRAM_SUPPORTED_FORMATS + "\n\n"
    epilog = epilog + "AUTHOR\n  " + PROGRAM_AUTHOR + "\n\n"
    epilog = epilog + "REPORTING BUGS\n  File a ticket at " + PROGRAM_URL + "\n\n"
    epilog = epilog + "COPYRIGHT\n  Copyright " + PROGRAM_COPYRIGHT + ".\n  License " + PROGRAM_LICENSE + "\n\n"
    epilog = epilog + "SEE ALSO\n  " + PROGRAM_SEE_ALSO + "\n\n"
    
    parser = argparse.ArgumentParser(
        description=description,
        epilog=epilog,
        formatter_class=RawTextHelpFormatter
    )

    parser.add_argument('file',
                            type=str,
                            help='Scan report to use',
                            default=None)
    
    parser.add_argument('-m', '--matched-text',
                            action='store_true',
                            help='output information about license matches',
                            default=False)
    
    parser.add_argument('-c', '--copyrights',
                            action='store_true',
                            help='output information about copyrights',
                            default=False)
    
    parser.add_argument('-cu', '--cumulative',
                            action='store_true',
                            help='outpur cumulative license information',
                            default=False)
    
    parser.add_argument('-l', '--license',
                            action='store_true',
                            help='output information about license',
                            default=False)
    
    parser.add_argument('-lf', '--license-filter',
                            type=str,
                            nargs="+",
                            help='filter on licenses containing argument',
                            default=[])
    
    parser.add_argument('-ff', '--file-filter',
                            type=str,
                            action='append',
                            nargs="+",
                            help='filter on file containing argument',
                            default=[])
    
    parser.add_argument('-fff', '--file-filter-file',
                            type=str,
                            action='append',
                            nargs="+",
                            help='filter on file containing file filters',
                            default=[])
    
    parser.add_argument('-f', '--format',
                            type=str,
                            help='output result in specified format, default is ' + OUTPUT_FORMAT_TEXT,
                            default=OUTPUT_FORMAT_TEXT)

    parser.add_argument('--version', '-V', action='version', version="{name}: {version}".format(name=scarfer_name, version=scarfer_version))

    parser.add_argument('-v', '--verbose',
                            action='store_true',
                            help='output verbose information to stderr',
                            default=False)
    args = parser.parse_args()

    return args


def _merge_file_filters(file_filter, file_filter_file):
    new_filters = []

    for filter_list in file_filter:
        for filter in filter_list:
            new_filters.append(filter)

    for file_name_list in file_filter_file:
        for file_name in file_name_list:
            f = open(file_name, 'r')
            for line in f.readlines():
                stripped_line = line.strip().replace("\n","")
                if not stripped_line.startswith("#") and len(stripped_line) > 0:
                    reg_exp = stripped_line
                    if not stripped_line.endswith("/"):
                        reg_exp = stripped_line + "$"
                    new_filters.append(reg_exp)
 
    return new_filters

def main():
    args = parse()

    # Create scan report reader 
    reader = ScanReportReader(args.file)

    # Create filters
    file_filter = _merge_file_filters(args.file_filter, args.file_filter_file)
    filters = create_filters(args.license_filter, file_filter)

    # Create output formatter
    formatter = FormatFactory.formatter(args.format)

    # Create settings map, to pass to reader (apply_filter)
    settings = Settings(args.copyrights, args.license, args.matched_text, args.cumulative)

    # Read report
    reader.read()

    # Filter the data in the report, with the filters
    reader.apply_filters(filters)
    filtered_files = reader.report()

    # Frmat the data 
    formatted_data = formatter.format(filtered_files, settings)

    # Print the data
    print(formatted_data)

if __name__ == '__main__':
    main()
    
