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

    def _apply_filter_file(self, filt, f):
        if filt.type == ScanReportFilterType.FILE:
            return re.search(filt.expr,f['path'])
        elif filt.type == ScanReportFilterType.LICENSE:
            for l in f['license']['expressions']:
                if re.search(filt.expr,l):
                    return True
            return False
        else:
            raise(ScanReportException("Unsupported filter type. This is weird."))
            
    def _apply_filters_file(self, f, filters):
        # If no filters, True means show all
        ret = True
        
        for filt in filters:
            filter_ret = self._apply_filter_file(filt, f)
            if self.operator == ScanReportFilterOperator.AND:
                ret  = ret and filter_ret
            elif self.operator == ScanReportFilterOperator.OR:
                ret  = ret or filter_ret
            else:
                raise(ScanReportException("Unsupported operator. This is weird."))

        return ret
        
    def apply_filters(self, filters=[], operator = ScanReportFilterOperator.AND):
        self.operator = operator
        
        keep_data = []
        for f in self.data:
            if not self._apply_filters_file(f, filters):
                pass
            else:
                keep_data.append(f)

        licenses = set()
        for f in keep_data:
            for lic in f['license']['expressions']:
                licenses.add(lic)

        license_string = " and ".join(licenses)
        licensing = Licensing()
        parsed = licensing.parse(license_string)

        report_data = {}
        report_data['files'] = keep_data
        report_data['meta'] = {}
        report_data['cumulative'] = {}
        report_data['cumulative']['license'] = parsed
                
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
            raise(ScanReportException("File not in a supported format"))

    def report(self):
        if self.report_data == None:
            self.apply_filters([])
        return self.report_data

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
        #print("tool: " + str(tool))
        if tool.lower() != "scancode-toolkit":
            print("Uh oh...")
            raise(ScanReportException("File not in Scancode format"))
        #print("OK")
    
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
                _file['copyrights'].append(c['value'])
                pass
            _file['license'] = []

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

