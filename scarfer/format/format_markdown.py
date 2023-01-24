
from scarfer.format.format_text import TextFormatter
#from scarfer.format.interface import FormatInterface
import os

class MarkdownFormatter(TextFormatter):

    def format_fixes(self, fixes, settings={}):
        excluded = [ 'Excluded files:\n' ]
        for f in fixes['excluded_files']:
            excluded.append(f' * {f["path"]}\n')
        missing = ['Missing license fixed:\n'] 
        for curation in fixes['missing_license']:
            missing.append(f' * {curation["file"]} -> {curation["curation"]}\n')
        return f'{os.linesep.join(excluded)}{os.linesep}{os.linesep.join(missing)}'

    def format_copyright_summary(self, report, settings={}):
        copyright_summary = set()
        for f in report['files']:
            for l in f['copyrights']:
                copyright_summary.add(f'{l}{os.linesep}')
        c_list = list(copyright_summary)
        c_list.sort()
        c_string = "\n".join(c_list)
        return f'{c_string}\n'

    
