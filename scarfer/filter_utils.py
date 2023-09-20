# SPDX-FileCopyrightText: 2023 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

from scarfer.analyzer import ScanReportFilter
from scarfer.analyzer import ScanReportFilterType

def _create_filter(expr, type):
    return ScanReportFilter(expr, type)

def _create_license_filter(expr):
    return _create_filter(expr, ScanReportFilterType.LICENSE)

def _create_copyright_filter(expr):
    return _create_filter(expr, ScanReportFilterType.COPYRIGHT)

def _create_file_filter(expr):
    return _create_filter(expr, ScanReportFilterType.FILE)

def create_filters(license_filter, copyright_filter, file_filter):
    filters = []
    for lf in license_filter:
        filters.append(_create_license_filter(lf))

    for lf in copyright_filter:
        filters.append(_create_copyright_filter(lf))

    for ff in file_filter:
        filters.append(_create_file_filter(ff))
    return filters
