import json

from scarfer.format.interface import FormatInterface

class JsonFormatter(FormatInterface):

    def format(self, report, settings={}):
        return json.dumps(report, indent=4)

