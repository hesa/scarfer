from enum import Enum
import re
from license_expression import Licensing, LicenseSymbol

from scarfer.format.factory import FormatFactory
#from format import FormatInterface


# expected result from read(), from the implementing classes
# ----------------------
# files: [
#   {
#     "path":       "tmp/tmp/apa.c",
#     "copyrights": [ "(c) 2009 Some One", "(c) 2001 Someone Elsie" ],
#     "license":    {
#       "expression": [ "mit or x11", "bsd" ],
#       "matches": [
#         {
#           "key":  "mit or x11",
#           "text": "This library is license under mit or x11"
#         }
#       ]
#     }
#  ]

#
# what to expect from report() - as a user
#
# {
#   "files": (see above)
#   "meta": {}
#   "cumulative": {
#     "license": "simplified license of all the combined"
#     "copytights": "combined copyrights"
#   }


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

            
class ScanReportReader:
    def __init__(self, file_name):
        self.file_name = file_name
        self.report_data = None

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
    
    def apply_filters(self, filters=[], exclude_filters=[]):

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
    
    def read(self):
        clazzes = [ FakeReportReader, FakeReportReader, ScancodeReportReader ]
        self.data = None
        for clazz in clazzes:
            try:
                self.data = clazz(self.file_name).read()
                break
            except Exception as e:
                pass
        if self.data == None:
            raise(ScanReportException(f"File {self.file_name} not in a supported format"))
        
    def report(self):
        if self.report_data == None:
            self.apply_filters([])
        return self.report_data
    
    def fixes(self):
        if self.report_data == None:
            self.apply_filters()
        return self.report_data['fixes']

    def raw_report(self):
        return self.report()['files']
    
    def __str__(self):
        ret = ["path: {name}".format(name=self.file_name)]
#        ret.append("operator: {operator}".format(operator=self.operator))
#        for f in filters:
#            ret.append("  {filter}".format(filter=f))
        return '\n'.join(ret)
            
class ScanReportException(Exception):

    def __init__(self, message=""):
        self.message = message
        super().__init__(self.message)

class FakeReportReader(ScanReportReader):

    def read(self):
        raise(ScanReportException("File not in fake format"))
        
class ScancodeReportReader(ScanReportReader):

    def check_file_format(self):
        headers = self.json_data['headers'][0]
        #print(str(headers))
        tool = headers['tool_name']
        self.scancode_format = headers.get('output_format_version', '')
        #print("tool: " + str(tool))
        if tool.lower() != "scancode-toolkit":
            raise(ScanReportException("File not in Scancode format"))

        if self.scancode_format == "2.0.0":
            self.copyright_value = "copyright"
        else:
            self.copyright_value = "value"
        
    
    def read(self):
        with open(self.file_name) as fp:
            import json
            self.json_data = json.load(fp)
            self.check_file_format()
            self.files = self.json_data['files']

        files = []
        for f in self.files:
            
            if not f['type'] == "file":
                continue
            
            _file = {}
            
            # path
            _file['path'] = f['path']
            
            # copyright
            _file['copyrights'] = []
            for c in f['copyrights']:
                #print(" c: " + str(c) + "  reading: " + self.copyright_value)
                _file['copyrights'].append(c[self.copyright_value])
                pass

            # license
            _file['license'] = {}
            matches = []
            for l in f['licenses']:
                matches.append({
                    "key": l['key'],
                    "text": l['matched_text']
                    })
            _file['license']['expressions'] = f['license_expressions']
            _file['license']['matches'] = matches

                
            files.append(_file)
            
        return files

