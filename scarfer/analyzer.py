import re
from enum import Enum
from license_expression import Licensing, LicenseSymbol



class ScanReportFilterOperator(Enum):
    AND = 1
    OR = 2

    def __str__(self):
        return str(self.value)
    
class ScanReportFilterType(Enum):
    FILE = 1
    LICENSE = 2
    
    def __str__(self):
        return str(self.value)

class ScanReportFilter:

    def __init__(self, _expr, _type = ScanReportFilterType.FILE):
        self.expr = _expr
        self.type = _type

    def __str__(self):
        return "expr: {_expr}, type: {_type}, ".format(
            _expr = self.expr,
            _type = self.type)

class Analyzer:

    def __init__(self, report):
        self.normaliazed_report = report
        self.data = report['files']
        self.schema = None

    def _apply_filter_file(self, filt, f):
        if filt.type == ScanReportFilterType.FILE:
            ret = re.search(filt.expr, f['path'])
            return ret != None
        elif filt.type == ScanReportFilterType.LICENSE:
            for l in f['license']['expressions']:
                if re.search(filt.expr,l):
                    return True
            return False
        else:
            raise(ScanReportException("Unsupported filter type. This is weird."))
            

    def _apply_filters_file(self, f, filters, filter_on_files):
        
        if len(filters) == 0:
            return True
        
        ret  = False
        
        for filt in filters:
            if filter_on_files:
                if filt.type == ScanReportFilterType.FILE:
                    ret = ret or self._apply_filter_file(filt, f)
                    
            else:
                if filt.type == ScanReportFilterType.LICENSE:
                    ret = ret or self._apply_filter_file(filt, f)

        return ret

    def _generic_filter_count(self, filters, filter_type):
        count = 0
        for filt in filters:
            if filt.type == filter_type:
                count += 1
        return count
        
    def _file_filter_count(self, filters):
        return self._generic_filter_count(filters, ScanReportFilterType.FILE)
    
    def _license_filter_count(self, filters):
        return self._generic_filter_count(filters, ScanReportFilterType.LICENSE)

    def __licenses_simplified(self, files):
        licenses = set()
        for f in files:
            for lic in f['license']['expressions']:
                licenses.add(lic)

        licenses_with_parenthesises = []
        for l in licenses:
            licenses_with_parenthesises.append(f" ( {l} )")
        #print(f"\nlic par:     {licenses_with_parenthesises}")
        license_string = " and ".join(licenses_with_parenthesises)
        licensing = Licensing()
        parsed = licensing.parse(license_string)
        if parsed is None:
            simplified = parsed
        else:
            simplified = parsed.simplify()
        return simplified

    def curate_missing_license(self, curated_license):
        for f in self.data:
            if f['license']['expressions'] == [ 'missing' ]:
                f['license']['expressions'] = curated_license
                self.report_data['fixes']['missing_license'].append(
                    {
                        'file': f['path'],
                        'curation': curated_license
                    }
                )
        
        self.report_data['cumulative']['license'] = self.__licenses_simplified(self.report_data['files'])
    
    def curate_file_license(self, files, curated_license):
        for curated_file in files:
            for f in self.data:
                if curated_file in f['path']:
                    #print(f'------ file: {f["path"]}')
                    orig = f['license']['expressions']
                    f['license']['expressions'] = [ curated_license ]
                    self.report_data['fixes']['curated_licenses'].append(
                        {
                            'file': f['path'],
                            'curation': curated_license,
                            'original': orig
                        }
                    )
        
        self.report_data['cumulative']['license'] = self.__licenses_simplified(self.report_data['files'])
    
    def apply_filters(self, filters=[], exclude_filters=[], package=""):

        # filter in on files
        if self._file_filter_count(filters) > 0:
            keep_data = []
            discard_data = []
            for f in self.data:
                #print("f: " + str(f['path']))
                if not self._apply_filters_file(f, filters, True):
                    discard_data.append(f)
                else:
                    keep_data.append(f)
        else:
            keep_data = self.data
            discard_data = []
            
        # filter in on licenses
        if self._license_filter_count(filters) > 0:
            ret_data = []
            for f in keep_data:
                if not self._apply_filters_file(f, filters, False):
                    discard_data.append(f)
                else:
                    ret_data.append(f)
            keep_data = ret_data

        # filter out on files
        if self._file_filter_count(exclude_filters) > 0:
            ret_data = []
            for f in keep_data:
                if not self._apply_filters_file(f, exclude_filters, True):
                    ret_data.append(f)
                else:
                    discard_data.append(f)
            keep_data = ret_data
            
        # filter out on licenses
        if self._license_filter_count(exclude_filters) > 0:
            ret_data = []
            for f in keep_data:
                if not self._apply_filters_file(f, exclude_filters, False):
                    ret_data.append(f)
                else:
                    discard_data.append(f)

            keep_data = ret_data
                    

        for f in keep_data:
            # If no license identified, mark as missing
            if f['license']['expressions'] == []:
                f['license']['expressions'] = [ "missing" ]

        report_data = {}
        report_data['files'] = keep_data
        report_data['fixes'] = {}
        report_data['fixes']['excluded_files'] = discard_data
        report_data['fixes']['missing_license'] = []
        report_data['fixes']['curated_licenses'] = []
        report_data['meta'] = {}
        report_data['cumulative'] = {}
        report_data['cumulative']['license'] = self.__licenses_simplified(keep_data)
        self.report_data = report_data

    def report(self):
        return self.report_data
        
    def fixes(self):
        if self.report_data == None:
            self.apply_filters()
        return self.report_data['fixes']
