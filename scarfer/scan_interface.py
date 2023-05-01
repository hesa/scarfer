import json
import jsonschema
import os

from scarfer.format.factory import FormatFactory
#from format import FormatInterface

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))


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

            
class ScanReportReader:
    
    def __init__(self, file_name):
        self.file_name = file_name
        self.report_data = None
        self.schema = None

    def validate(self):
        if not self.schema:
            schema_file = os.path.join(os.path.join(SCRIPT_DIR, "var"), "normalized-scan.json")
            with open(schema_file, 'r') as f:
                self.schema = json.load(f)
            jsonschema.validate(instance=self.data, schema=self.schema)
        
    def read(self):
        clazzes = [ FakeReportReader, ScancodeReportReader ]
        self.data = None
        for clazz in clazzes:
            try:
                self.data = clazz(self.file_name).read()
                break
            except Exception as e:
                pass
        if self.data == None:
            raise(ScanReportException(f"File {self.file_name} not in a supported format"))
        
        return self.data

    def __str__(self):
        ret = ["path: {name}".format(name=self.file_name)]
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
        tool = headers['tool_name']
        self.scancode_format = headers.get('output_format_version', '')
        if tool.lower() != "scancode-toolkit":
            raise(ScanReportException(f'File not in Scancode format. Tool={tool}'))

        if self.scancode_format == "2.0.0":
            self.copyright_value = "copyright"
        else:
            self.copyright_value = "value"
        self.tool = headers['tool_name']
        self.tool_version = headers['tool_version']
    
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
            _file['path'] = f.get('path','')
            _file['sha1'] = f.get('sha1','')
            _file['md5'] = f.get('md5','')
            _file['sha256'] = f.get('sha256','')

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
                if 'key' in l and 'matched_text' in l:
                    matches.append({
                        "key": l['key'],
                        "text": l['matched_text']
                    })
            _file['license']['expressions'] = f['license_expressions']
            _file['license']['matches'] = matches
            
            files.append(_file)

        meta = {
            "scanner": {
                "tool_name": self.tool,
                "tool_version": self.tool_version,
                "tool_output_format": self.scancode_format
            }
        }

        return {
            "files": files,
            "meta": meta
        }
