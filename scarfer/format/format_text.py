from scarfer.format.interface import FormatInterface

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

    def _format_cumulative(self, report, settings):
        ret = []
        cumulative = report['cumulative']
        ret.append(" * license: {_license}".format(_license=cumulative['license']))
        return "\n".join(ret)
        
    
    def format(self, report, settings):

        if settings.get('license_summary') or settings.get('copyright_summary'):
            res = ""
            if settings.get('license_summary'):
                license_summary = set()
                for f in report['files']:
                    for l in f['license']['expressions']:
                        license_summary.add(l)
                res += f'Licenses:\n { " AND ".join(license_summary)}\n'

            if settings.get('copyright_summary'):
                copyright_summary = set()
                for f in report['files']:
                    for l in f['copyrights']:
                        copyright_summary.add(l)
                c_list = list(copyright_summary)
                c_list.sort()
                c_string = "\n".join(c_list)
                res += f'Copyrights:\n{c_string}\n'
            return res
        elif settings.get('cumulative'):
            return self._format_cumulative(report, settings)
        else:
            results = [
                "Files:\n----------------------------",
                self._format_files(report, settings),
            ]
            return "\n".join(results)


        
        
