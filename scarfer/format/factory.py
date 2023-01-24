from scarfer.format.format_json import JsonFormatter
from scarfer.format.format_yaml import YamlFormatter
from scarfer.format.format_text import TextFormatter
from scarfer.format.format_markdown import MarkdownFormatter


class FormatFactory:

    @staticmethod
    def formatter(format):
        if format.lower() == "json":
            return JsonFormatter()
        elif format.lower() == "yaml" or format.lower() == "yaml":
            return YamlFormatter()
        elif format.lower() == "text" or format.lower() == "txt":
            return TextFormatter()
        elif format.lower() == "markdown" or format.lower() == "md":
            return MarkdownFormatter()
