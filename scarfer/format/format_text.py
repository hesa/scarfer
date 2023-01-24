from scarfer.format.interface import FormatInterface
import os

class TextFormatter(FormatInterface):

    def _format_file(self, f, settings):
        ret = []
        
        copyrights = settings.get('copyrights')
        licenses = settings.get('licenses')
        matches = settings.get('matches')

        if licenses:
            ret.append("{path}: {license}".format(path=f['path'], license=str(f['license']['expressions'])))
        else:
            ret.append("{path}".format(path=f['path']))
                
        if copyrights:
            for cr in f['copyrights']:
                ret.append(" * {c}".format(c=cr))
        if matches:
            for m in f['license']['matches']:
                ret.append("--- {match} --- ".format(match=m['key']))
                ret.append("{text}".format(text=m['text']))
            
        return "\n".join(ret)

    def _format_files(self, report, settings):
        ret = []
        for f in report['files']:
            ret.append(self._format_file(f, settings))
        return "\n".join(ret)

    def format(self, report, settings):
        results = [
            "Files:\n----------------------------",
            self._format_files(report, settings),
        ]
        return "\n".join(results)

    def format_fixes(self, fixes, settings={}):
        excluded = [ 'Filtered out:' ]
        for f in fixes['excluded_files']:
            excluded.append(f' * {f["path"]}')
        missing = ['Missing license fixed:'] 
        for curation in fixes['missing_license']:
            missing.append(f' * {curation["file"]} -> {curation["curation"]}')
        return f'{os.linesep.join(excluded)}{os.linesep}{os.linesep.join(missing)}'

    def format_cumulative(self, report, settings={}):
        ret = []
        cumulative = report['cumulative']
        ret.append(f"Cumulative license: {cumulative['license']}")
        return "\n".join(ret)
        
    def format_license_summary(self, report, settings={}):
        license_summary = set()
        for f in report['files']:
            for l in f['license']['expressions']:
                license_summary.add(l)
        return f'License:\n { " AND ".join(license_summary)}\n'

    def format_copyright_summary(self, report, settings={}):
        copyright_summary = set()
        for f in report['files']:
            for l in f['copyrights']:
                copyright_summary.add(l)
        c_list = list(copyright_summary)
        c_list.sort()
        c_string = "\n".join(c_list)
        return f'Copyrights:\n{c_string}\n'



        
        
