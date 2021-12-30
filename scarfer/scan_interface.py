from enum import Enum
import re


#
# RESULT
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
    def __init__(self, file_name, filters=[], operator = ScanReportFilterOperator.AND):
        self.file_name = file_name
        self.filters = filters
        self.operator = operator

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
            
    def _apply_filters_file(self, f):
        # If no filters, True means show all
        ret = True
        
        for filt in self.filters:
            filter_ret = self._apply_filter_file(filt, f)
            if self.operator == ScanReportFilterOperator.AND:
                ret  = ret and filter_ret
            elif self.operator == ScanReportFilterOperator.OR:
                ret  = ret or filter_ret
            else:
                raise(ScanReportException("Unsupported operator. This is weird."))

        return ret
        
    def apply_filters(self):
        keep_data = []
        for f in self.data:
            if not self._apply_filters_file(f):
                #print("remove file: " + f['path'] + ": " + str(len(self.data)))
                #self.data.remove(f)
                #print(str(len(self.data)))
                pass
            else:
                keep_data.append(f)
                print("keep   file: " + f['path'] + ": " + str(len(keep_data)))

        self.kept_data = keep_data
    
    def read(self):
        clazzes = [ FakeReportReader, FakeReportReader, ScancodeReportReader ]
        self.data = None
        for clazz in clazzes:
            print("trying: " + str(clazz))
            try:
                self.data = clazz(self.file_name).read()
                break
            except:
                print("pass...")
                pass
        if self.data == None:
            raise(ScanReportException("File not in a supported format"))

        print("size: " + str(len(self.data)))
        self.apply_filters()
        print("size: " + str(len(self.kept_data)))

        return self.kept_data

    def __str__(self):
        ret = ["path: {name}".format(name=self.file_name)]
        ret.append("operator: {operator}".format(operator=self.operator))
        for f in self.filters:
            ret.append("  {filter}".format(filter=f))
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
        print(str(headers))
        tool = headers['tool_name']
        print("tool: " + str(tool))
        if tool.lower() != "scancode-toolkit":
            raise(ScanReportException("File not in Scancode format"))
        
    
    def read(self):
        with open(self.file_name) as fp:
            import json
            print("slakj 1")
            self.json_data = json.load(fp)
            print("slakj 2")
            self.check_file_format()
            print("slakj 3")
            self.files = json_data['files']

        files = []
        for f in self.files:
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

# 
# test code
#
        
def main():
    print("begin...")

    reader = ScancodeReportReader("apa.txt")
    print("reader:   " + str(reader))

    filter_type = ScanReportFilterType.FILE
    print("type:   " + str(filter_type))
    
    file_filter = ScanReportFilter("cairo-xcb")
    print("filter:   " + str(file_filter))
    
    license_filter = ScanReportFilter("x11", ScanReportFilterType.LICENSE)
    print("filter:   " + str(file_filter))
    
    reader = ScanReportReader("example-data/cairo-1.16.0-scan.json", [file_filter, license_filter])
    print("reader:   " + str(reader))

    files = reader.read()
    
    print("data:   ")
    for f in files:
        print(" * " + f['path'] + ": " + str(f['license']['expressions']))

    print("end...")

if __name__ == '__main__':
    main()


#    TODO
#
# - calculate concluded license
# - simplify license expression
# - formats for printout
