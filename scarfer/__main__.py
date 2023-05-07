#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

from argparse import RawTextHelpFormatter
import argparse
import json
import sys
import os

from scarfer.format.factory import FormatFactory
from scarfer.scan_interface import ScanReportReader
from scarfer.scan_interface import ScanReportException
from scarfer.analyzer import Analyzer
from scarfer.format.interface import Settings
from scarfer.filter_utils import create_filters
from scarfer.config import scarfer_version
from scarfer.config import scarfer_name
from scarfer.config import DEFAULT_FILE_EXCLUDE_FILE

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

PROGRAM_NAME = scarfer_name
PROGRAM_VERSION = scarfer_version
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

    description = f'NAME\n  {PROGRAM_NAME} ({PROGRAM_VERSION})\n\n'
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
    
    parser.add_argument('--normalize',
                        action='store_true',
                        help='quit after scan report normalization and outpout result',
                        default=False)
    
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
    
    parser.add_argument('-ls', '--license-summary',
                            action='store_true',
                            help='output license summary',
                            default=False)
    
    parser.add_argument('-cs', '--copyright-summary',
                            action='store_true',
                            help='output copyright summary',
                            default=False)
    
    parser.add_argument('-il', '--include-license',
                            type=str,
                            nargs="+",
                            action='append',
                            help='filter on licenses containing argument',
                            default=[])
    
    parser.add_argument('-el', '--exclude-license',
                            type=str,
                            action='append',
                            nargs="+",
                            help='filter out licenses containing argument',
                            default=[])
    
    parser.add_argument('-if', '--include-file',
                            type=str,
                            action='append',
                            nargs="+",
                            help='filter on file containing argument',
                            default=[])
    
    parser.add_argument('-ef', '--exclude-file',
                            type=str,
                            action='append',
                            nargs="+",
                            help='filter out on file containing argument',
                            default=[])
    
    parser.add_argument('-iff', '--include-file-file',
                            type=str,
                            action='append',
                            nargs="+",
                            help='filter on file containing file filters',
                            default=[])
    
    parser.add_argument('-eff', '--exclude-file-file',
                            type=str,
                            action='append',
                            nargs="+",
                            help='filter out on file containing file filters',
                            default=[])
    
    parser.add_argument('-dde', '--disable-default-excludes',
                        action='store_true',
                        help=f'Disable exclusion of files as specified in {DEFAULT_FILE_EXCLUDE_FILE}')

    parser.add_argument('-cml', '--curate-missing-license',
                        type=str,
                        dest='curate_missing_license',
                        action='append',
                        help='curate missing license for a file with',
                        default=[])
    
    parser.add_argument('-cfl', '--curate-file-license',
                        type=str,
                        dest='curate_file_license',
                        nargs="+",
                        action='append',
                        help='curate license for a file with: file1 file2 curated-license',
                        default=[])
    
    parser.add_argument('-f', '--format',
                            type=str,
                            help='output result in specified format, default is ' + OUTPUT_FORMAT_TEXT,
                            default=OUTPUT_FORMAT_TEXT)

    parser.add_argument('--output-fixes',
                        dest='output_fixes',
                        action='store_true',
                        help='output files filtered out and curations')

    parser.add_argument('--version', '-V', action='version', version="{name}: {version}".format(name=scarfer_name, version=scarfer_version))

    parser.add_argument('-v', '--verbose',
                            action='store_true',
                            help='output verbose information to stderr',
                            default=False)
    
    parser.add_argument('-oc', '--output--config',
                        action='store_true',
                        dest="output_config",
                        help='output command line options as configuration',
                        default=False)
    
    parser.add_argument('--config',
                        type=str,
                        dest="read_config",
                        help='read configuration from file',
                        default=False)
    
    args = parser.parse_args()

    return args


def _merge_file_filters(clude_file, clude_file_file):
    new_filters = []

    for include_list in clude_file:
        for filter in include_list:
            new_filters.append(filter)

    for file_name_list in clude_file_file:
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

def flatten_lists(lists):
    new_list = []
    for l in lists:
        for elem in l:
            new_list.append(elem)
    return new_list

def _output_config(args):
    config = {
        'tool_name': scarfer_name,
        'tool_version': scarfer_version,
#        "copyrights": args.copyrights,
#        "cumulative": args.cumulative,
        "curate_missing_license": args.curate_missing_license,
        "curate_file_license": args.curate_file_license,
        "exclude_file": args.exclude_file,
        "exclude_file_file": args.exclude_file_file,
        "exclude_license": args.exclude_license,
        "file": args.file,
#        "format": args.format,
        "include_file": args.include_file,
        "include_file_file": args.include_file_file,
        "include_license": args.include_license,
#        "license": args.license,
#        "license_summary": args.license_summary,
#        "matched_text": args.matched_text
        }
    return json.dumps(config, indent=4)
        
def _read_config(config_file, args):
    new_args = {}
        
    for key in args.__dict__:
        new_args[key] = vars(args).get(key)

    if not args.read_config:
        return new_args
    
    with open(config_file) as conf:
        confs = json.load(conf)

    for key, value in confs.items():
        new_args[key] = value

    return new_args

    # 0xDEADC0DE
    for key in args.__dict__:
        args_val = vars(args)[key]
        conf_val = new_args.get(key)
        print(f'{key}: {args_val} : {conf_val}')
        if args_val == conf_val:
            #print(f'key {key} same')
            pass
        elif key not in args:
            print(f'key {key} not found')
            pass
        else:
            print(f'key {key} differs:  conf: {conf_val}')
            if isinstance(conf_val,list):
                new_args[key] += args_val
            else:
                new_args[key] = args_val
            print(f'key {key} now: {new_args[key]}')
        

def main():
    
    args = parse()

    if args.output_config:
        print(_output_config(args))
        sys.exit(0)
        
    args = _read_config(args.read_config, args)

    # Create scan report reader 
    reader = ScanReportReader(args['file'])

    # Get a normalized report
    normalized_report = reader.read()
    if args['normalize']:
        reader.validate()
        print(json.dumps(normalized_report, indent=4))
        sys.exit(0)
    
    include_license = flatten_lists(args['include_license'])
    exclude_license = flatten_lists(args['exclude_license'])
    #exclude_file = flatten_lists(args['exclude_file)
    
    # Create filters
    include_files = _merge_file_filters(args['include_file'], args['include_file_file'])
    filters = create_filters(include_license, include_files)

    if args['disable_default_excludes']:
        pass
    else:
        args['exclude_file_file'].append([DEFAULT_FILE_EXCLUDE_FILE])
    exclude_files = _merge_file_filters(args['exclude_file'], args['exclude_file_file'])
    exclude_filters = create_filters(exclude_license, exclude_files)
    
#    print(f"include_files:   {include_files}")
#    print(f"include_filters: {filters}")
#    print(f"exclude_files:   {exclude_files}")
#    print(f"exclude_filters: {exclude_filters}")
    
    # Create output formatter
    formatter = FormatFactory.formatter(args['format'])

    # Create settings map, to pass to apply_filter
    settings = Settings(args['copyrights'], args['license'], args['matched_text'], args['cumulative'], args['license_summary'], args['copyright_summary'])

    # Filter the data in the report, with the filters
    analyzer = Analyzer(normalized_report)
    analyzer.apply_filters(filters, exclude_filters)

    #
    # Curations
    # 
    if args['curate_missing_license']:
        analyzer.curate_missing_license(args['curate_missing_license'])
    if args['curate_file_license']:
        for curation in args["curate_file_license"]:
            length = len(curation)
            nr_files = length -1
            curated_license = curation[nr_files]
            files = curation[0:nr_files]
            analyzer.curate_file_license(files, curated_license)
            
    filtered_files = analyzer.report()

    # Format the data
    if args['copyright_summary'] or args['license_summary']:
        formatted_data_list = []
        if args['copyright_summary']:
            formatted_data_list.append(formatter.format_copyright_summary(filtered_files, settings))
        if args['license_summary']:
            formatted_data_list.append(formatter.format_license_summary(filtered_files, settings))
        formatted_data = "\n".join(formatted_data_list)
    elif args['cumulative']:
        formatted_data = formatter.format_cumulative(filtered_files, settings)
    elif args['output_fixes']:
        formatted_data = formatter.format_fixes(reader.fixes(), settings)
    else:
        formatted_data = formatter.format(filtered_files, settings)

    # Print the data
    print(formatted_data)

if __name__ == '__main__':
    main()
    
