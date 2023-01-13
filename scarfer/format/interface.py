
class Settings:
    def __init__(self, copyrights = False, licenses = False, matches = False, cumulative = False, license_summary = False, copyright_summary = False):
        self.settings_map = {}
        self.settings_map['copyrights'] = copyrights
        self.settings_map['licenses'] = licenses
        self.settings_map['matches'] = matches
        self.settings_map['cumulative'] = cumulative
        self.settings_map['license_summary'] = license_summary
        self.settings_map['copyright_summary'] = copyright_summary

    def get(self, key):
        #print(" get " + key + " from " + str(self.settings_map) + " =====> " + str(self.settings_map.get(key, False)))
        return self.settings_map.get(key, False)

class FormatInterface:

    def __init__(self):
        return

    def format(self, report, settings={}):
        return 






