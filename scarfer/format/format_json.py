import json

from scarfer.format.interface import FormatInterface

class JsonFormatter(FormatInterface):

    def format(self, report, settings={}):
        return json.dumps(report['files'], indent=4)

    def format_cumulative(self, report, settings={}):
        ret = []
        cumulative = report['cumulative']
        ret.append(" * license: {_license}".format(_license=cumulative['license']))
        return "\n".join(ret)
        
    def format_license_summary(self, report, settings={}):
        license_summary = set()
        for f in report['files']:
            for l in f['license']['expressions']:
                license_summary.add(l)
        return json.dumps({ "license": f'{ " AND ".join(license_summary)}' })

    def format_copyright_summary(self, report, settings={}):
        copyright_summary = set()
        for f in report['files']:
            for l in f['copyrights']:
                copyright_summary.add(l)
        c_list = list(copyright_summary)
        c_list.sort()
        c_string = "\n".join(c_list)
        return json.dumps({ "copyrights": f'\n{c_string}' })



        
        
