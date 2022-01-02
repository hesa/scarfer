
class Settings:
    def __init__(self, copyrights = False, licenses = False, matches = False):
        self.settings_map = {}
        self.settings_map['copyrights'] = copyrights
        self.settings_map['licenses'] = licenses
        self.settings_map['matches'] = matches

    def get(self, key):
        #print(" get " + key + " from " + str(self.settings_map) + " =====> " + str(self.settings_map.get(key, False)))
        return self.settings_map.get(key, False)

class FormatInterface:

    def __init__(self):
        return

    def format(self, report, settings={}):
        return 






