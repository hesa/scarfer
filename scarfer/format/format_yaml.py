# SPDX-FileCopyrightText: 2023 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import yaml

from scarfer.format.interface import FormatInterface

class YamlFormatter(FormatInterface):

    def format(self, report, settings={}):
        return yaml.dump(report)
