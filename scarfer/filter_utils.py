from scarfer.scan_interface import ScanReportFilter
from scarfer.scan_interface import ScanReportFilterType

def _create_filter(expr, type):
    return ScanReportFilter(expr, type)

def _create_license_filter(expr):
    return _create_filter(expr, ScanReportFilterType.LICENSE)
    
def _create_file_filter(expr):
    return _create_filter(expr, ScanReportFilterType.FILE)

def create_filters(license_filter, file_filter):
    filters = []
    for lf in license_filter:
        filters.append(_create_license_filter(lf))
        
    for ff in file_filter:
        filters.append(_create_file_filter(ff))
    return filters
