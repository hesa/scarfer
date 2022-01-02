import yaml
        
from scarfer.format.interface import FormatInterface

class YamlFormatter(FormatInterface):

    def format(self, report, settings={}):
        return yaml.dump(report)
