# SPDX-FileCopyrightText: 2023 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

from scarfer.format.interface import FormatInterface
from scarfer.format.format_utils import summarize_license
import os
from flict.flictlib.arbiter import Arbiter

class TextFormatter(FormatInterface):

    def _format_file(self, f, settings):
        ret = []

        copyrights = settings.get('copyrights')
        licenses = settings.get('licenses')
        matches = settings.get('matches')

        if licenses:
            ret.append("{path}: {license}".format(path=f['path'], license=str(f['license']['expressions'])))
        else:
            ret.append("{path}".format(path=f['path']))

        if copyrights:
            for cr in f['copyrights']:
                ret.append(" * {c}".format(c=cr))
        if matches:
            for m in f['license']['matches']:
                ret.append("--- {match} --- ".format(match=m['key']))
                ret.append("{text}".format(text=m['text']))

        return "\n".join(ret)

    def _format_files(self, report, settings):
        ret = []
        for f in report['files']:
            ret.append(self._format_file(f, settings))
        return "\n".join(ret)

    def format(self, report, settings):
        results = [
            "Files:\n----------------------------",
            self._format_files(report, settings),
        ]
        return "\n".join(results)

    def format_fixes(self, fixes, settings={}):
        excluded = ['Filtered out:']
        for f in fixes['excluded_files']:
            excluded.append(f' * {f["path"]}')
        missing = ['Missing license fixed:']
        for curation in fixes['missing_license']:
            missing.append(f' * {curation["file"]} -> {curation["curation"]}')
        return f'{os.linesep.join(excluded)}{os.linesep}{os.linesep.join(missing)}'

    def format_cumulative(self, report, settings={}):
        ret = []
        cumulative = report['cumulative']
        ret.append(f"Cumulative license: {cumulative['license']}")
        return "\n".join(ret)

    def format_license_summary(self, report, settings={}):
        license_summary = set()
        for fi in report['files']:
            for le in fi['license']['expressions']:
                license_summary.add(le)
        license_summary = summarize_license(list(license_summary))
        if settings.get('simplify'):
            arbiter = Arbiter()
            license_summary = arbiter.simplify_license(license_summary)['simplified']
        return f'License:\n {license_summary}\n' # noqa: E231

    def format_copyright_summary(self, report, settings={}):
        copyright_summary = set()
        for fi in report['files']:
            for cop in fi['copyrights']:
                copyright_summary.add(cop)
        c_list = list(copyright_summary)
        c_list.sort()
        c_string = "\n".join(c_list)
        return f'Copyrights:\n{c_string}\n' # noqa: E231
