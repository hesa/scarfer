# SPDX-FileCopyrightText: 2023 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

from scarfer.format.format_text import TextFormatter
import os

class MarkdownFormatter(TextFormatter):

    def format_fixes(self, fixes, settings={}):
        excluded = ['Excluded files:\n']
        for f in fixes['excluded_files']:
            excluded.append(f' * {f["path"]}\n')
        missing = ['Missing license fixed:\n']
        for curation in fixes['missing_license']:
            missing.append(f' * {curation["file"]} -> {curation["curation"]}\n')
        return f'{os.linesep.join(excluded)}{os.linesep}{os.linesep.join(missing)}'

    def format_copyright_summary(self, report, settings={}):
        copyright_summary = set()
        for f in report['files']:
            for cop in f['copyrights']:
                copyright_summary.add(f'{cop}{os.linesep}')
        c_list = list(copyright_summary)
        c_list.sort()
        c_string = "\n".join(c_list)
        return f'{c_string}\n'
